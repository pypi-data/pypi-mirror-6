#    Bat-man - YouTube video batch downloader
#    Copyright (C) 2013 ElegantMonkey
#
#    This program is free software: you can redistribute it and/or modify
#    it under the terms of the GNU General Public License as published by
#    the Free Software Foundation, either version 3 of the License, or
#    (at your option) any later version.
#
#    This program is distributed in the hope that it will be useful,
#    but WITHOUT ANY WARRANTY; without even the implied warranty of
#    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
#    GNU General Public License for more details.
#
#    You should have received a copy of the GNU General Public License
#    along with this program.  If not, see [http://www.gnu.org/licenses/].


"""This module implements an interface to Pafy objects with batch-ing and
conversion in focus.

"""

import re
import tempfile
import batman.pafy
import os
import subprocess
import sys
import random
from multiprocessing import Pool, freeze_support
from batman import definitions
from batman.definitions import path_with
from batman.codec_interface import base_codec
from batman.codec_interface import libmp3lame
import logging

class DownloaderAndEncoder(object):
    """DownloaderAndEncoder is a instance of a video being downloaded and encoded.
    Internally, it uses batman.pafy.Pafy(self.video) to grab it's data and
    to download.
    
    Encoding uses command-line functions(bad, so bad) to call ffmpeg to extract
    .WAVs, and LAME to convert them to MP3.
    
    """
    on_download_progress = None
    
    def __init__(self, url, outfolder, quality, VBRquality=2):
        """Creates a new DownloaderAndEncoder object.
        
        Keyword arguments:
        url -- The YouTube video url.
        outfolder -- The path of the destination folder.
        quality -- YouTube video quality(e.g. 360, 480, 720).
        VBRquality -- The -V argument passed to LAME, i.e. the quality setting
        for VBR. Ranges from 0 to 9 - lower is better quality, higher is better
        compression. (default: 2)"""
        for i in range(3):
            try:
                self.video = batman.pafy.Pafy(url)
                break
            except RuntimeError:
                raise RuntimeError("Invalid URL")
            except:
                if i != 2: continue
                else: raise RuntimeError("Couldn't load video")
        
        if definitions.WINDOWS:
            # Windows doesn't supports two programs accessing the same file, then
            # we need to close it now, and, on __del__, unlink them.
            self.original_video = tempfile.NamedTemporaryFile(delete=False)
            self.original_video.close()
        else:
            self.original_video = tempfile.NamedTemporaryFile()
        
        # != = XOR
        if definitions.OPTIONS.audioCodecEnabled != definitions.OPTIONS.videoCodecEnabled:
            if definitions.OPTIONS.audioCodecEnabled:
                self.codec = definitions.OPTIONS.audioCodec()
            else:
                self.codec = definitions.OPTIONS.videoCodec()
            self.solo_encoding = True
        elif definitions.OPTIONS.audioCodecEnabled and definitions.OPTIONS.videoCodecEnabled:
            self.interactor = definitions.OPTIONS.interactor()
            self.solo_encoding = False
        else:
            raise RuntimeError("No codecs are set.")
        
        if self.solo_encoding:
            self.mp3_out = outfolder + "/" + \
                           self.codec.make_valid_file_name_from_caption(self.video.title)
        else:
            self.mp3_out = outfolder + "/" + \
                           self.interactor.make_valid_file_name_from_caption(self.video.title)
        self.quality = quality
        self.VBRquality = VBRquality
        self.download_progress = None # Not downloading.
    
    def set_outfolder(self, outfolder):
        """Changes the destination of the converted video."""
        if self.solo_encoding:
            self.mp3_out = outfolder + "/" + \
                           self.codec.make_valid_file_name_from_caption(self.video.title)
        else:
            self.mp3_out = outfolder + "/" + \
                           self.interactor.make_valid_file_name_from_caption(self.video.title)
    
    def _progress_callback(self, total, bytesdone, pct, rate, eta):
        self.download_progress = (total, bytesdone, pct, rate, eta)
        try:
            self.on_download_progress(self)
        except TypeError:
            pass
    
    def download(self):
        """Downloads the video(doesn't encodes)."""
        current_choice = None
        # Try to use Pafy audio-only downloading.
        if self.solo_encoding and base_codec.is_codec_an_audio_codec(self.codec):
            current_choice = self.video.getbestaudio()
        # Select best match for quality and, for preference, mp4.
        if current_choice == None:
            for stream in self.video.streams:
                stream_res = int(stream.resolution.split("x")[0])
                
                if self.quality == stream_res and stream.extension == "mp4": # I can't believe it... Perfect!
                    current_choice = stream
                    break
            
                if current_choice == None:
                    current_choice = stream
                    continue
                else:
                    # If the current is mp4 and the one we're trying isn't, fuck it,
                    # we want the mp4 one.
                    if current_choice.extension == "mp4" and stream.extension != "mp4":
                        continue
                    
                    current_res = int(current_choice.resolution.split("x")[0])
                    # Is this a better choice?
                    if abs(self.quality - stream_res) < abs(self.quality - current_res): # Some mathmagics
                        current_choice = stream
        
        for i in range(0, 3):
            try:
                self.download_progress = None
                current_choice.download(quiet=True,
                                        callback=self._progress_callback,
                                        filepath=self.original_video.name)
                break
            except:
                if i != 2: continue
                else:
                    raise RuntimeError("Last try failed. Exiting")

    def __del__(self):
        if definitions.WINDOWS:
            logging.debug("Deleting temporary files %s and %s", self.original_video.name, self.wav_file.name)
            os.unlink(self.original_video.name)
            os.unlink(self.wav_file.name)

# No pickles anymore :X
def _helper_encode_solo(codec, orig_p, mp3_o, VBRquality, ticket):
    codec.encode(mp3_o, orig_p)
    return ticket

def _helper_encode_interaction(interactor, orig_p, mp3_o, VBRquality, ticket):
    interactor.encode(mp3_o, orig_p)
    return ticket

# Up, up, down, down, left, right, left, right, (B, A?)
class DownloadAndEncodeMarshaller(object):
    """DownloadAndEncodeMarshaller is a manager of DownloadAndEncode objects."""
    
    on_video_start_download = None
    on_video_start_encoding = None
    on_video_progress = None
    on_video_finish = None
    
    NON_EXISTANT = 1
    PENDING = 2
    DOWNLOADING = 3
    ENCODING = 4
    FINISHED = 5
    NOT_FOUND = 6

    def __init__(self, let_invalid_url_errors_pass=True):
        self.all = []
        self.pending = []
        self.downloading = []
        self.encoding = {}
        self.encoder_pool = Pool(processes=2)
        self.finished = []
        self.event_starter_quit = False
        self.let_invalid_url_errors_pass = let_invalid_url_errors_pass
        self.reload_codecs()
        
    def reload_codecs(self):
        if definitions.OPTIONS.audioCodecEnabled != definitions.OPTIONS.videoCodecEnabled:
            if definitions.OPTIONS.audioCodecEnabled:
                self.codec = definitions.OPTIONS.audioCodec()
            else:
                self.codec = definitions.OPTIONS.videoCodec()
            self.solo_encoding = True
        elif definitions.OPTIONS.audioCodecEnabled and definitions.OPTIONS.videoCodecEnabled:
            self.interactor = definitions.OPTIONS.interactor()
            self.solo_encoding = False
        else:
            raise RuntimeError("No codecs are set.")
    
    def find_state_of_video(self, video):
        if video not in self.all: return self.NON_EXISTANT
        elif video in self.pending: return self.PENDING
        elif video in self.downloading: return self.DOWNLOADING
        elif video in self.encoding.values(): return self.ENCODING
        elif video in self.finished: return self.FINISHED
        else: return self.NOT_FOUND
    
    def add_video_to_download(self, url, outfolder, quality, VBRquality=2):
        try:
            downloaderAndEncoder = DownloaderAndEncoder(url, outfolder, quality, VBRquality)
        except RuntimeError as e:
            if str(e) == "Invalid URL":
                if self.let_invalid_url_errors_pass: return
            raise
        downloaderAndEncoder.on_download_progress = self.on_video_progress
        self.all.append(downloaderAndEncoder)
        self.pending.append(downloaderAndEncoder)
    
    # Use tickets to know which encode is being done.
    def _generate_ticket(self):
        while True:
            # And, if you have more than 10000 videos processing... Oh, c'mon, what the fuck are you doing?
            n = random.randrange(0, 10000)
            if n not in self.encoding: return n
    
    def _finish_encode(self, ticket):
        try:
            v = self.encoding[ticket]
            self.finished.append(v)
            del self.encoding[ticket]
            self.on_video_finish(self, v)
        except IndexError:
            pass
    
    # BLOCKING FUNCTION
    def start(self):
        while len(self.pending) > 0:
            self.downloading.append(self.pending.pop(0))
            try:
                if self.on_video_start_download != None:
                    self.on_video_start_download(self, self.downloading[-1])
                self.downloading[-1].download()
                ticket = self._generate_ticket()
                # Don't fuck everything now, GC.
                self.encoding[ticket] = self.downloading.pop(-1)
                if self.on_video_start_encoding != None:
                    self.on_video_start_encoding(self, self.encoding[ticket], ticket)
                
                if self.solo_encoding:
                    helper = _helper_encode_solo
                    args = (self.codec,
                            self.encoding[ticket].original_video.name,
                            self.encoding[ticket].mp3_out,
                            self.encoding[ticket].VBRquality,
                            ticket)
                else:
                    helper = _helper_encode_interaction
                    args = (self.interactor,
                            self.encoding[ticket].original_video.name,
                            self.encoding[ticket].mp3_out,
                            self.encoding[ticket].VBRquality,
                            ticket)
                self.encoder_pool.apply_async(helper,
                                              args,
                                              callback=lambda t: self._finish_encode(t),
                                              error_callback=lambda e: print(e))
            except RuntimeError:
                raise # Shouldn't let it pass, but, for now, let it pass with a -small- message
    
    # Starts downloading then, at the end, wait for a event, that can either restart
    # the download or finish the function
    def event_starter(self, event):
        while not self.event_starter_quit:
            self.start()
            event.clear() # If set events went called after that, clear them.
            # If, between this gap, videos were put in the queue
            # Restart the function
            if len(self.pending) > 0:
                continue
            event.wait()
    
    def __del__(self):
        # self.encoding needs a "special" treatment MUAHAHAHA
        # Hopefully this will exclude temporary files on Windows. Hopefully.
        for l in [self.all, self.pending, self.downloading, self.finished]:
            for video in l:
                del video
            l.clear() # Overkill!
        
        for video in self.encoding.values():
            del video
        
        del self.encoding

def batch_download(txt_file, outfolder, quality, VBRquality):
    marshall = DownloadAndEncodeMarshaller()
    for line in txt_file:
        line = line.rstrip()
        if line == "": continue
        marshall.add_video_to_download(line, outfolder, quality, VBRquality)
    
    marshall.start()
    marshall.encoder_pool.close()
    marshall.encoder_pool.join()

def main():
    freeze_support()
    
    txt_file = sys.argv[1]
    outfolder = sys.argv[2]
    quality = int(sys.argv[3])
    VBRquality = int(sys.argv[4])
    
    batch_download(open(txt_file, "r"), outfolder, quality, VBRquality)
    
if __name__ == "__main__":
    main()
    
