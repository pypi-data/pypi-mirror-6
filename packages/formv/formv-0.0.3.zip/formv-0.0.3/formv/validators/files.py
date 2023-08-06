#!/usr/bin/python
# -*- coding: utf-8 -*-

# This module is part of formv and is released under the MIT License: 
# http://www.opensource.org/licenses/mit-license.php 

import os, zipfile, logging, errno, sys
from shutil import copy2, move
from formv.validators.base import VBase
from formv.validators.strings import VString
from formv.exception import Invalid
from formv.utils.iterators import StreamIterator
from formv.utils.imaging import *
from formv.utils.fileinfo import (image_mime_types, BaseFileInfo, 
                                  ExistingFileInfo, ReusedFileInfo, 
                                  UploadedFileInfo) 
from formv.utils import extract_text as _
from formv.utils.compat import PY2, PY3
if PY2:
    import Image
if PY3:
    try:
        import Image
    except ImportError:        
        from PIL import Image
        
log = logging.getLogger(__name__)

__all__ = ('VImprintImage','VTextToImage','VUploadFile','VWatermarkImage',)

class ZipFileError(Exception):
    pass

class VUploadFile(VBase):
    """
    Validates and transforms uploaded files (input type='file') based on 
    their mime-type. Documents can be compressed (zip archive), images can 
    be resized and a thumbnail can be created for each one. Returns an 
    UploadedFileInfo object (see formv.utils.fileinfo), that contains all 
    the necessary information to be saved in a database.
    
    Parameters as follows:

    temp_dir:
        Folder path where the cgi.FieldStorage like file will be stored prior 
        to any processing.
    mime_types:
        A dictionary of mime-types and their associated settings:        
        max_size:
            Maximum file-size for this mime-type (integer)
        compress: 
            Boolean value specifying if the file will be compressed (zip)
        resize_to:
            Pictures will be resized to this size (tuple of length 2)  
        thumbnail:        
            A thumbnail of this size will be created for an image 
            (tuple of length 2)
        move_to:
            Final location folder
        backup_to:    
            Backup folder of the original file       
        
    Examples:
    
        mime_types configuration:
                     
            non-image mime-types:
            
            {'text/plain':
                {'max_size':1024*1024, 
                 'compress':True, 
                 'move_to':'/some/path',
                 'backup_to':'/some/backup_dir'},
             'text/csv':
                 {'max_size':1024*2048, 
                  'compress':True, 
                  'move_to':'/some/other/path',
                  'backup_to':'/some/backup_dir'}, ... 
             }

            image mime-types:
            
            {'image/gif': 
                {'max_size':1024*2048, 
                 'resize_to':(640,480), 
                 'thumbnail':(160,120), 
                 'move_to':'/some/public_dir',
                 'backup_to':'/some/backup_dir'},
             'image/jpeg': 
                 {'max_size':1024*2048, 
                  'resize_to':(640,480), 
                  'thumbnail':(160,120), 
                  'move_to':'/some/public_dir',
                  'backup_to':'/some/backup_dir'}, ...
            }

        
        def setup_mime_types():        
            mime_types = {}
            
            for t in ('text/plain','text/csv','text/html','text/xml', 
                      'application/pdf','application/rtf',
                      'application/msword','application/xml',):
                mime_types[t] = {'max_size':1024*1024, 'compress':True, 
                                 'move_to':'/srv/www/my_site/storage',
                                 'backup_to':'/srv/www/my_site/backup',}
        
            for t in ('image/gif','image/jpeg','image/pjpeg',
                      'image/pipeg','image/png','image/x-png',):
                mime_types[t] = {'max_size':1024*1024, 'resize_to':(640,480), 
                                 'thumbnail':(160,120),
                                 'move_to':'/srv/www/my_site/public',
                                 'backup_to':'/srv/www/my_site/backup',}
            return mime_types
                        
        class WebForm(VSchema):    
            fields = {                
                VUploadFile(mime_types=setup_mime_types())
                ...
            }
        
    """
    def __init__(self, mime_types, temp_dir='/tmp/formv', **kw):
        VBase.__init__(self, **kw)
        self.temp_dir = temp_dir
        self.mime_types = mime_types
                
        if not os.path.isdir(self.temp_dir):
            try:
                os.makedirs(self.temp_dir)
            except OSError as e:
                if e.errno != errno.EEXIST:
                    raise                
    
    def _validate(self, value):  
        self.messages.update({'invalid': _('Invalid upload, errors occurred'),
                              'mime-type': _('Invalid upload, file-type not accepted'),
                              'file-size': _('Invalid upload, file-size too large')})
        
        if isinstance(value, ReusedFileInfo):
            return value
        
        if not hasattr(value, 'filename'):  # - empty upload field
            return value

        f = UploadedFileInfo(value, self.temp_dir)
        
        if f.mime_type not in self.mime_types.keys():
            f.file_object = value.file = None
            raise Invalid(self.message('mime-type'), value)
        if f.file_size > int(self.mime_types[f.mime_type]['max_size']):
            f.file_object = value.file = None
            raise Invalid(self.message('file-size'), value)

        try:
            self._write_file(f)
            f.file_object = value.file = None
            
            if self.mime_types[f.mime_type].get('backup_to'):
                backup_to_path = self.mime_types[f.mime_type].get('backup_to') 
                if not os.path.isdir(backup_to_path):
                    raise ValueError(_('No such directory: %s') % backup_to_path)
                s = os.path.join(self.temp_dir, f.file_name)
                d = os.path.join(backup_to_path, f.file_name)
                copy2(s, d)
            
            if self.mime_types[f.mime_type].get('compress'):            
                zinfo, zip_err = self._compress_file(f)
                if zip_err:
                    raise ZipFileError(zip_err)
                f.file_ext = '.zip'
                f.zip_size = zinfo.compress_size 
    
            if self.mime_types[f.mime_type].get('resize_to'): 
                resolution = self.mime_types[f.mime_type].get('resize_to')
                self._resize_image(f, resolution, mode='resize')
            
            if self.mime_types[f.mime_type].get('thumbnail'): 
                resolution = self.mime_types[f.mime_type].get('thumbnail')
                self._resize_image(f, resolution, mode='thumbnail')

            if self.mime_types[f.mime_type].get('move_to'):
                move_to_path = self.mime_types[f.mime_type].get('move_to')   
                if not os.path.isdir(move_to_path):
                    raise ValueError(_('No such directory: %s') % move_to_path)
             
                f.dir_path = move_to_path
                
                if self.mime_types[f.mime_type].get('compress'): 
                    s = os.path.join(self.temp_dir, f.zip_name)
                    d = os.path.join(f.dir_path, f.zip_name)
                else:
                    s = os.path.join(self.temp_dir, f.file_name)
                    d = os.path.join(f.dir_path, f.file_name)
                move(s, d)

                if self.mime_types[f.mime_type].get('thumbnail'):
                    s = os.path.join(self.temp_dir, f.thumb_name)
                    d = os.path.join(f.dir_path, f.thumb_name)
                    move(s, d)
                    
        except Exception as e:
            log.error(e, exc_info=sys.exc_info())
            f.file_object = value.file = None
            for p in (f.file_path, f.zip_path, f.thumb_path):
                self._remove_file(p)
            raise Invalid(self.message('invalid'), value)
        
        return f
        
    def _write_file(self, fo):
        f = open(os.path.join(self.temp_dir, fo.file_name), 'wb')
        s = StreamIterator(fo.file_object)
        try: 
            for d in s:
                f.write(d)
        finally:
            f.close()
            s.close()

    def _compress_file(self, f):       
        """
        To unzip:
        zf = zipfile.ZipFile(f.zip_path, 'r', zipfile.ZIP_DEFLATED)
        return zf.open(f.orig_name, 'rU')
        """ 
        fp = os.path.join(self.temp_dir, f.file_name)
        zp = os.path.join(self.temp_dir, f.guid_name + '.zip')                                   
               
        zf = zipfile.ZipFile(zp, 'w', zipfile.ZIP_DEFLATED)
        zf.write(fp, f.orig_name, zipfile.ZIP_DEFLATED)
        zf.close()        
        self._remove_file(fp)
        
        zf = zipfile.ZipFile(zp, 'r', zipfile.ZIP_DEFLATED)            
        return (zf.getinfo(f.orig_name), zf.testzip())        
    
    def _resize_image(self, f, r, mode):
        if not isinstance(r, (list, tuple)) or len(r) != 2:
            raise ValueError(_('Resolution must be a tuple of length 2'))        
        if not mode in ('resize', 'thumbnail'):
            msg = _('Image mode must be one of [resize, thumbnail], received %s')
            raise ValueError(msg % mode)
        
        s = d = os.path.join(self.temp_dir, f.file_name)
        i = Image.open(s)
        
        if mode == 'resize':
            if r[0] >= 1024 or r[1] >= 768:
                i.resize(r, Image.ANTIALIAS)
            else:
                i.resize((1024,768), Image.NEAREST)         
                i.resize(r, Image.ANTIALIAS)
                
        if mode == 'thumbnail':
            d = os.path.join(self.temp_dir, f.thumb_name)
            if r[0] >= 1024 or r[1] >= 768:
                i.thumbnail(r, Image.ANTIALIAS)
            else:
                i.thumbnail((1024,768), Image.NEAREST)
                i.thumbnail(r, Image.ANTIALIAS)
        i.save(d)

    def _remove_file(self, fp):
        try:
            if fp and os.path.isfile(fp): 
                os.remove(fp)
        except Exception as e:
            log.error(e)


class VWatermarkImage(VBase):
    """ 
    Applies a watermark to an image. The watermark can be a text or another 
    image that will be superimposed over the uploaded image. 
    
    The transparency of the watermark can be manipulated by adjusting the 
    alpha color levels, by adjusting the opacity or a combination of both. 
    
    The watermark arguments are as follows:    
    type:
        Watermark type. Can be 'text' or 'image'. 
    mode:
        Watermark layout mode. Can be 'tile', 'scale' or 'fixed'.
    text: 
        The text to be printed on the watermark layer. Used if type is 'text'.
    layer: 
        Watermark layer size. The text will be imprinted on this layer. 
        Should be a tuple of length 2. Used if type is 'text'.
    font: 
        Font face and size to be used (see ImageFont). Used if type is 'text'.
    color: 
        Font color to be used (see ImageColor). Used if type is 'text'.
    file:
        Path to watermark image file. Used if type is 'image'
    margin:
        Position from top-left where the watermark will be applied. 
        Used if type is 'fixed'. Should be a tuple of length 2.
    opacity:
        A floating point value between 0 and 1 specifying the opacity 
        of the watermark.  
    angle:
        A floating point value between 0 and 360 specifying 
        the watermark rotation.
    """
    def __init__(self, type='text', mode='tile', text=None, layer=(160,120), 
                 font=None, color=(0,0,0,255), file=None, margin=(0,0), 
                 opacity=.3, angle=0, **kw):        
        VBase.__init__(self, **kw)
        self.type = type
        self.mode = mode
        self.text = text        
        self.layer = layer
        self.font = font
        self.color = color        
        self.file = file 
        self.margin = margin
        self.opacity = opacity
        self.angle = angle

    def _validate(self, value):
        self.messages.update({'invalid': _('Invalid upload, errors occurred')})   
        try:                                      
            if not isinstance(value, BaseFileInfo):
                msg = _('Argument must be of BaseFileInfo type, received %s')
                raise TypeError(msg % type(value))
            if isinstance(value, ReusedFileInfo):
                return value
            if value.mime_type in image_mime_types and value.zip_name is None:
                watermark(image_path=value.file_path, 
                          type=self.type, 
                          mode=self.mode, 
                          text=self.text, 
                          layer=self.layer,
                          font=self.font,
                          color=self.color,
                          file=self.file,
                          margin=self.margin, 
                          opacity=self.opacity,
                          angle=self.angle)
            return value
        except Exception as e:
            log.error(e, exc_info=sys.exc_info())
            raise Invalid(self.message('invalid'), value)
        

class VImprintImage(VBase):    
    """ 
    Applies an imprint to an image. An imprint is slightly different than 
    a watermark as the imprint position will be exact vs the fixed watermark 
    position that will be relative to the watermark layer size.
    
    The transparency of the imprint can be manipulated by adjusting the 
    alpha color levels, by adjusting the opacity or a combination of both. 
    
    The imprint arguments are as follows:        
    text: 
        The text to be printed on the watermark layer.
    font: 
        Font to be used (see ImageFont).
    color: 
        Font color to be used (see ImageColor).
    float:
        Text float position.
        Should be one of: ('top-left','top-center','top-right',
                           'center-left','center','center-right',
                           'bottom-left','bottom-center','bottom-right')
    margin:
        Should contain the margin from float position where the 
        imprint will be applied. Tuple of length 2.
    opacity:
        A floating point value between 0 and 1 specifying the opacity 
        of the imprint  
    angle:
        A floating point value between 0 and 360 specifying the text rotation        
    """    
    def __init__(self, text, font=None, color=(0,0,0,255), float='bottom-right', 
                 margin=(25,25), opacity=1, angle=0, **kw):        
        VBase.__init__(self, **kw)
        self.text = text
        self.font = font
        self.color = color
        self.float = float 
        self.margin = margin
        self.opacity = opacity
        self.angle = angle

    def _validate(self, value):
        self.messages.update({'invalid': _('Invalid upload, errors occurred')})
        try:
            if not isinstance(value, BaseFileInfo):
                msg = _('Argument must be of BaseFileInfo type, received %s')
                raise TypeError(msg % type(value))
            if isinstance(value, ReusedFileInfo):
                return value
            if value.mime_type in image_mime_types and value.zip_name is None:
                imprint(value.file_path, 
                        text=self.text, 
                        font=self.font, 
                        color=self.color, 
                        float=self.float, 
                        margin=self.margin, 
                        opacity=self.opacity,
                        angle=self.angle)        
            return value
        except Exception as e:
            log.error(e, exc_info=sys.exc_info())
            raise Invalid(self.message('invalid'), value)


class VTextToImage(VString):
    """
    Writes a given text onto an image and returns the text and the image info.

    Arguments are as follows:
    dir_path:
        Folder where the generated image will be saved
    image_size:
        Image size. Tuple of length 2
    image_format:
        Image format
    bgcolor:
        Image background color
    font:
        Font that will be used to draw the text (see ImageFont).
    color:
        Font color (see ImageColor).
    float:
        Text float position.
        Should be one of: ('top-left','top-center','top-right',
                           'center-left','center','center-right',
                           'bottom-left','bottom-center','bottom-right')
    margin:
        Should contain the margin from float position where the 
        text will be applied. Tuple of length 2.
    """    
    def __init__(self, dir_path, image_size=(300,25), image_format='PNG', 
                 bgcolor=(255,255,255,255), font=None, color=(0,0,0,255),
                 float='center-left', margin=(5,0), **kw):        
        VString.__init__(self, **kw)
        self.dir_path = dir_path        
        self.image_format = image_format 
        self.image_size = image_size 
        self.bgcolor = bgcolor
        self.font = font
        self.color = color
        self.float = float
        self.margin = margin

    def _validate(self, value):
        self.messages.update({'invalid': _('Text to Image transformation failed')})
        try:        
            value = VString._validate(self, value)
            image_path = text_to_image(value, dir_path=self.dir_path,        
                                       image_size=self.image_size,
                                       image_format=self.image_format,                                                     
                                       bgcolor=self.bgcolor,
                                       font=self.font, 
                                       color=self.color,
                                       float=self.float,
                                       margin=self.margin)            
            return (value, ExistingFileInfo(image_path))
        except Invalid:
            raise
        except Exception as e:
            log.error(e, exc_info=sys.exc_info())
            raise Invalid(self.message('invalid'), value)
        
