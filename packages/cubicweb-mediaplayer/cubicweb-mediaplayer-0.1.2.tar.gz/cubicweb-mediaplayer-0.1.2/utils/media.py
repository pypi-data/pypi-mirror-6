# -*- coding: utf-8 -*-
# copyright 2013 LOGILAB S.A. (Paris, FRANCE), all rights reserved.
# contact http://www.logilab.fr -- mailto:contact@logilab.fr
#
# This program is free software: you can redistribute it and/or modify it under
# the terms of the GNU Lesser General Public License as published by the Free
# Software Foundation, either version 2.1 of the License, or (at your option)
# any later version.
#
# This program is distributed in the hope that it will be useful, but WITHOUT
# ANY WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
# FOR A PARTICULAR PURPOSE. See the GNU Lesser General Public License for more
# details.
#
# You should have received a copy of the GNU Lesser General Public License along
# with this program. If not, see <http://www.gnu.org/licenses/>.

"""cubicweb-mediaplayer utils for media"""

from subprocess import call, Popen, PIPE
from tempfile import TemporaryFile
import re

from ID3 import ID3

from cubicweb import Binary
from cubes.mediaplayer.utils import TemporaryDir

def _ensure_file(stream):
    """Return a real file with the content of the stream
    If the stream is already a file, the same object is returned.
    """
    if hasattr(stream, 'fileno'):
        return stream
    else:
        stream.seek(0)
        temp = TemporaryFile()
        temp.write(stream.read())
        temp.seek(0)
        return temp

def id3infos(sound):
    if isinstance(sound, (Binary, file)):
        return ID3(sound)
    return ID3(sound.data)

# Audio reencoding logic ##############################################

SOUND_FORMATS = {'oga':
                 # codec        #bitrates
                 ('ogg', 'libvorbis', ''), # or codec vorbis .
                 'mp3':
                 ('mp3', 'libmp3lame', '128') # aac
                 }

def get_audio_biterate(sound):
    return flv_meta(sound)['audiodatarate']

def get_sound_formats(sound):
    outputs = {'mp3': None, 'oga': None}
    if sound.data_format == 'audio/mpeg':
        # audio_biterate = get_audio_biterate(sound)
        # if audio_biterate < 128:
        #     # no need to reencode the mp3
        return {'mp3': sound.data,
                'oga' : None}
    return outputs

def reencode_sound(sound, outputs):
    """
    preduce .mp3 and .ogg files for a file
    ffmpeg -y -i a.mp3 -acodec libvorbis -ab -aq 3 output.ogg
    ffmpeg -y -i a.mp3 -acodec libmp3lame -ab 123k output.mp3
    avconv -y -i toto.aiff -f mp3 aac -acodec aac -strict experimental -ab 128k output.mp3
    avconv -i /data/projects/fevis/sag1/1_audio.aiff -y -f ogg -acodec libvorbis -aq 3 toto.oga

    """
    if not sound.data.getvalue():
        for attr, value in outputs.iteritems():
            outputs[attr] = Binary('')
        return results
    inputfile = sound.fspath('data')
    with TemporaryDir() as tmp:
        for attr, value in outputs.iteritems():
            if value is not None:
                continue
            format, audio_codec, bitrates = SOUND_FORMATS[attr]
            output_filename = tmp.filepath(suffix='.%s' % attr)
            cmd = ['avconv',
                   # overwrite output files
                   '-y',
                   # input
                   '-i', inputfile,
                   '-f',  format,
                   ]
            # add codec
            cmd.extend([ '-acodec', audio_codec])
            if audio_codec == 'aac':
                cmd.extend(['-strict', 'experimental'])
            if bitrates :
                cmd.extend([ '-ab', '%sk' % bitrates])
            else:
                cmd.extend(['-aq', '3'])
            cmd.append(output_filename)
            _quiet_call(cmd, cwd=tmp.root)
            print ' %s : finish %s encoding' % (repr(inputfile), attr)
            outputs[attr] = Binary.from_file(output_filename)
    return outputs


def set_bytes_attr(entity, attr, content, format):
    title = entity.title or entity.data_name or u''
    data = {
        attr: content,
        attr+'_format': format,
        attr+'_name': title
    }
    entity.cw_set(**data)

def parse_ff_output(re, stderr, video):
    values = {}
    for attr , regexpr in re.items():
        match = regexpr.search(stderr)
        if match is not None:
            values[attr] = int(float(match.group(1)))
    return values

# Video reencoding logic ##############################################

#: ALL possible format we want to encode to:
VIDEO_FORMATS = [
    # (  'low',    'low', {'x':  320},  64,  190,     220,    1835, 'medium',  True),
    # (  'std', 'medium', {'x':  512},  96,  350,     400,    1835, 'medium',  True),
    # ( 'high',   'high', {'y':  480}, 128,  730,     800,    1835, 'medium', False),
    # ( '720p',     'hd', {'y':  720}, 128, 1500,    1800,    1835, 'medium', False),
    # ('1080p', 'fullhd', {'y': 1080}, 160, 3900,    4400,    1835, 'medium', False),
    # attribute name, format_name, ..... video_codec, audio_codec
    ('mp4',           'mp4',  'medium',   {'x':  512},  96,  350,     400,    1835, 'medium',  True, 'libx264', 'aac'),
    ('ogg',           'ogv',  'medium',  {'x':  512},  96,  350,     400,    1835, 'medium',  True, 'libtheora', 'libvorbis'),
    # ('webm',          'webm',  'medium',  {'x':  512},  96,  350,     400,    1835, 'medium',  True, 'libtheora', 'libvorbis'),
    ]



VIDEO_SIZE = (720, 406)

def normalise_size(current, target):
    width, height = current
    max_width, max_height = target
    ratio = max(float(width)  / max_width, float(height) / max_height)
    finalwidth  = int(round(width / ratio))
    finalheight = int(round(height / ratio))
    return finalwidth, finalheight

def get_video_formats():
    return VIDEO_FORMATS

def video_filter_format(video, formats=VIDEO_FORMATS):
    """choose which formats we actually need to re-encode and properly sets the size

    for each format, we compare the dimensions of the base video and the existing parameter
    of the format

    - the original dimensions are greater than those needed
    OR
    - the original dimensions are smaller but the video bitrate is greater

    Other formats are ignored
    Then we calculate the missing size parameter of the format and store it

    Candidates are picked from FORMATS in the same module.

    yield format tuple
    """
    for fmt in formats:
        name, eattr, attr, size, abr, vbr, max_vbr, bf, preset, force, video_codec, audio_codec = fmt
        # filter format from quality
        # if the "size check" fails, use bitrate (of known)
        # XXX use proper ratio data
        def greater_dim(a, b):
            return (a in size and size[a] > b)

        def greater_vbr(a):
            def has_vbr(a):
                return getattr(a, 'videodatarate', None)
            return ( not has_vbr(a) or ( has_vbr(a) and vbr > a.videodatarate ) )
        if not force:
            if greater_dim('x', video.width) or greater_dim('y', video.height):
                if greater_vbr(video):
                    continue

        # we do not want to modify the original dict
        calc_size = size.copy()
        if not greater_dim('x', video.width):
            print 'resize'
            x, y = normalise_size((video.width, video.height), VIDEO_SIZE)
            calc_size = {'x': x + (x % 2), 'y': y + (y % 2)}
            print 'old x, y', (video.width, video.height)
            print 'new x, y', calc_size['x'], calc_size['y']
        else:
            if 'x' in size:
                y = (video.height * size['x']) / video.width
                calc_size['y'] = y + (y % 2) # height must be a multiple of 2
            else:
                x = (video.width  * size['y']) / video.height
                calc_size['x'] = x + (x % 2) # width must be a multiple of 2
        yield (name, eattr, attr, calc_size, abr, vbr, max_vbr, bf, preset, force, video_codec, audio_codec)

def _output_parameters(outputs, passlogfilenames, firstpass=False):
    """generates the command-line options for ffmpeg

    The command-line options are generated for each selected output and their values
    are taken from the ``FORMATS`` table.
    For now, every output uses the 'medium' preset because of the satisfying quality/cost ratio,
    in the future we will probably want customized preset files for each outputs.

    passlogfilenames is a dict containing the names of pass log files for each output

    If firstpass is True, adapts the options for the firstpass of the 2pass encoding
    """
    # hard written value for now

    parameters = []
    for filename, format in outputs.iteritems():
        _format, _, _, size, audio_bitrate, video_bitrate, max_video_bitrate, bufsize, preset, force, video_codec, audio_codec = format
        # audio parameters
        parameters.extend([
                '-acodec', audio_codec,
                '-ab', '%ik' % audio_bitrate,
                ])
        if audio_codec == 'aac': # codec 'aac' is still experimental
            parameters.extend(['-strict', 'experimental',
                               ])
        parameters.extend([
                '-vcodec', video_codec,
                '-vb', '%ik' % video_bitrate,
                '-minrate', '0',
                '-maxrate', '%ik' % max_video_bitrate,
                '-bufsize', '%ik' % bufsize,
                '-s', '%(x)ix%(y)i' % size,
                '-f', _format,
                ])
        # multipass & output parameters
        parameters.extend([
            '-preset', preset,
            '-pass', firstpass and '1' or '2',
            '-passlogfile', passlogfilenames[filename],
             filename,
             ])
    return parameters

_FAIL_TEXT = """SubCall failed (returned with status %i)
%s
=== STDOUT ============================
%s
=== STDERR ============================
%s
"""
def _quiet_call(args, **kwargs):
    """Run and ffmpeg conversion with the profived argument

    Do not display output except on failure.

    Raise a RuntimeError on failure. the stdout and std of the process will be
    available in the exception message.

    The call is nice and ioniced.
    """
    call = []
    ### nice to save cpu
    call.extend(['nice', '-n', '19'])
    ### ionice to save IO
    # call.extend(['ionice', '-c', '3']) #idle do something when nobody does
    call.extend(['ionice', '-c', '2', '-n', '7']) # best effort lowest priority

    call.extend(args)
    sub = Popen(call, stdout=PIPE, stderr=PIPE, **kwargs)
    out, err = sub.communicate()
    if sub.returncode:
        formated_call = " ".join("%s" % p for p in call)
        raise RuntimeError(_FAIL_TEXT % (sub.returncode, formated_call, out, err))


def reencode_video(video, outputs):
    """reencode a video in multiple format.

    """
    ### actual ffmpeg call
    results = {}
    # file is empty, do not proceed
    if not video.data.getvalue():
        for _, _fmt in outputs.iteritems():
            results[_fmt[1]] = (_fmt[0], Binary(''))
        return results
    inputfile = video.fspath('data')
    call = ['avconv', '-i', inputfile]
    # overwrite file for test
    call.append('-y')
    # we need pass log files common to the 2 passes
    passlogfilenames = {}
    tmp_outputs = {}
    with TemporaryDir() as tmp:
        for _fmt, _format in outputs.iteritems():
            tmp_filename = tmp.filepath(suffix='.%s' % _fmt)
            passlogfilenames[tmp_filename] = tmp.filepath(suffix='.fpf')
            tmp_outputs[tmp_filename] = _format
        firstpass  = _output_parameters(tmp_outputs, passlogfilenames, firstpass=True)
        secondpass = _output_parameters(tmp_outputs, passlogfilenames, firstpass=False)
        # error_stream = open('/dev/null')
        print ' %s : first pass encoding' % repr(inputfile)
        _quiet_call(call + firstpass, cwd=tmp.root)
        print ' %s : second pass encoding' % repr(inputfile)
        _quiet_call(call + secondpass, cwd=tmp.root)
        print ' %s : finish encoding' % repr(inputfile)
        for input_path, fmt in tmp_outputs.items():
            if fmt[0] == 'mp4':
                output_path = tmp.filepath(suffix='.%s' % _fmt)
                set_moov_atom(input_path, output_path)
            else:
                output_path = input_path
            output = Binary.from_file(output_path)
            results[fmt[1]] = (fmt[0], output)
        return results

def set_moov_atom(input_path, output_path):
    """sets the moov atom to the beginning of a media file

    the moov atom is used by buffering/streaming logics to know when to
    start playing the media file and allow the progressive download on mp4 files
    """
    # qt-faststart is provided with ffmpeg/avconv
    cmd = ['qt-faststart', input_path, output_path]
    sub = Popen(cmd, stdout=PIPE, stderr=PIPE)
    out, err = sub.communicate()
    if sub.returncode:
        raise RuntimeError('Unable to set the moov atom of %s\n'
                           'qt-faststart returned with status %s\n'
                           '== STDOUT =====\n'
                           '%s\n'
                           '== STDERR =====\n'
                           '%s' % (output_path, sub.returncode, out, err))

#  META on FILES ###########################################################################

RE_DURATION = re.compile(r'Duration: (\d\d):(\d\d):(\d\d\.\d\d)')
RE_END = r'%s\s*:\s*(\d+)'

META_RE = {'width': re.compile(RE_END % r'width'),
                 'height': re.compile(RE_END % r'height'),
                 'videodatarate': re.compile(RE_END % r'videodatarate'),
                 'audiodatarate': re.compile(RE_END % r'audiodatarate'),
                 'framerate': re.compile(RE_END % r'framerate'),
                 }

OTHER_META_RE = {'width': re.compile(r': Video: .*, (\d+)x\d+'),
                 'height': re.compile(r': Video: .*, \d+x(\d+)'),
                 'videodatarate': re.compile(r': Video: .*, (\d+) kb/s'),
                 'framerate': re.compile(r': Video: .*, (\d+\.?\d*) tbr'),
                 #... : Video: h264 (High) (avc1 / 0x31637661), yuv420p, 390x390 [SAR 1:1 DAR 1:1], 500 kb/s, 25 fps, 25 tbr, 90k tbn, 50 tbc
                 'audiodatarate': re.compile(r': Audio: .*, (\d+) kb/s'),
                 #... : Audio: aac (mp4a / 0x6134706D), 44100 Hz, stereo, s16, 128 kb/s
                 }

def flv_meta(stream):
    """Return the duration in second, width, height, videodatarate,
    audiodatarate, framerate of the audio or video stream in argument"""
    # for cleaner version: check http://code.activestate.com/recipes/457406/
    cmd = [# input from stdin
        'avprobe', 'pipe:0',
        ]
    values = {}
    media = _ensure_file(stream)
    ffmpeg = Popen(cmd, stdin=media, stdout=PIPE, stderr=PIPE)
    stdout, stderr = ffmpeg.communicate()
    assert ffmpeg.returncode == 0, ffmpeg.returncode
    match = RE_DURATION.search(stderr)
    if match is None:
        if 'Unsupported media codec' in stderr:
            # raise ValueError('Unsupported VideoCodec for stream %s'% media)
            print 'Unsupported VideoCodec for stream %s' % media

        else:
            # raise RuntimeError('Could not find Duration information in ffmmpeg output for media %s:\n%s' % (media, stderr))
            print 'Could not find Duration information in ffmmpeg output for steam %s:\n%s' % (media, stderr)
        values['length'] = 0
    else:
        values['length'] = (int(match.group(1)) * (60 ** 2)
                            + int(match.group(2)) * 60
                            + int(float(match.group(3))))

    values.update(parse_ff_output(META_RE, stderr, media))
    values.update(parse_ff_output(OTHER_META_RE, stderr, media))
    media.close()
    return values
