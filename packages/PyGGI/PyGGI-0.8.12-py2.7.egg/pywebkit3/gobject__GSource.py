# Copyright, John Rusnak, 2012
    # This code binding is available under the license agreement of the LGPL with
    # an additional constraint described below,
    # and with the understanding that the webkit API is copyright protected
    # by Apple Computer, Inc. (see below).
    # There is an  additional constraint that any derivatives of this work aimed
    # at providing bindings to GObject, GTK, GDK, or WebKit be strictly
    # python-only bindings with no native code.
    # * THIS SOFTWARE IS PROVIDED ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    #
    # ******************************************************
    # For the API:
    # /*
    # * Copyright (C) 2006 Apple Computer, Inc.  All rights reserved.
    # *
    # * Redistribution and use in source and binary forms, with or without
    # * modification, are permitted provided that the following conditions
    # * are met:
    # * 1. Redistributions of source code must retain the above copyright
    # *    notice, this list of conditions and the following disclaimer.
    # * 2. Redistributions in binary form must reproduce the above copyright
    # *    notice, this list of conditions and the following disclaimer in the
    # *    documentation and/or other materials provided with the distribution.
    # *
    # * THIS SOFTWARE IS PROVIDED BY APPLE COMPUTER, INC. ``AS IS'' AND ANY
    # * EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE
    # * IMPLIED WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR
    # * PURPOSE ARE DISCLAIMED.  IN NO EVENT SHALL APPLE COMPUTER, INC. OR
    # * CONTRIBUTORS BE LIABLE FOR ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL,
    # * EXEMPLARY, OR CONSEQUENTIAL DAMAGES (INCLUDING, BUT NOT LIMITED TO,
    # * PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES; LOSS OF USE, DATA, OR
    # * PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON ANY THEORY
    # * OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
    # * (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE
    # * OF THIS SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.
    # */
from ctypes import *
from gtk3_types import *
from gobject_types import *
    
    
"""Derived Pointer Types"""
__GtkRcStyle = POINTER(c_int)
__GdkGeometry = POINTER(c_int)
_WebKitNetworkResponse = POINTER(c_int)
_GdkPixbuf = POINTER(c_int)
__GtkRequisition = POINTER(c_int)
_GtkRcStyle = POINTER(c_int)
__GtkRegionFlags = POINTER(c_int)
__WebKitDOMNode = POINTER(c_int)
_GtkWindow = POINTER(c_int)
__cairo_font_options_t = POINTER(c_int)
__JSValue = POINTER(c_int)
_JSContext = POINTER(c_int)
_GtkIconFactory = POINTER(c_int)
__GdkAtom = POINTER(c_int)
__GdkTimeCoord = POINTER(c_int)
_GdkColor = POINTER(c_int)
__GtkWidgetPath = POINTER(c_int)
__GClosure = POINTER(c_int)
__GMainContext = POINTER(c_int)
_GdkDisplay = POINTER(c_int)
__GtkStyleProvider = POINTER(c_int)
_GtkDialog = POINTER(c_int)
__WebKitWebWindowFeatures = POINTER(c_int)
_JSObject = POINTER(c_int)
_GBytes = POINTER(c_int)
_GScanner = POINTER(c_int)
_PangoFont = POINTER(c_int)
_GtkStyleContext = POINTER(c_int)
_GMainContext = POINTER(c_int)
__GtkTextBuffer = POINTER(c_int)
_GtkTargetList = POINTER(c_int)
__WebKitWebSettings = POINTER(c_int)
_GdkAppLaunchContext = POINTER(c_int)
__GObject = POINTER(c_int)
__PangoLayout = POINTER(c_int)
_WebKitWebBackForwardList = POINTER(c_int)
_GtkOffscreenWindow = POINTER(c_int)
__GParamSpec = POINTER(c_int)
__PangoAttrIterator = POINTER(c_int)
_GtkIconSet = POINTER(c_int)
_GtkSelectionData = POINTER(c_int)
_GtkWindowGroup = POINTER(c_int)
_JSGlobalContext = POINTER(c_int)
_PangoLogAttr = POINTER(c_int)
__PangoContext = POINTER(c_int)
__JSPropertyNameArray = POINTER(c_int)
_WebKitWebSettings = POINTER(c_int)
__PangoFont = POINTER(c_int)
__GtkPathPriorityType = POINTER(c_int)
__JSClass = POINTER(c_int)
__WebKitWebHistoryItem = POINTER(c_int)
_JSValue = POINTER(c_int)
__GtkSettings = POINTER(c_int)
_GSource = POINTER(c_int)
__PangoFontMap = POINTER(c_int)
__JSString = POINTER(c_int)
__PangoAttrList = POINTER(c_int)
_PangoMatrix = POINTER(c_int)
__GSource = POINTER(c_int)
_GtkApplication = POINTER(c_int)
__PangoAnalysis = POINTER(c_int)
_PangoFontDescription = POINTER(c_int)
__GdkCursor = POINTER(c_int)
_GtkBorder = POINTER(c_int)
_WebKitWebInspector = POINTER(c_int)
_GOptionGroup = POINTER(c_int)
__GScanner = POINTER(c_int)
__GtkWidgetClass = POINTER(c_int)
__GdkEventKey = POINTER(c_int)
__GdkDisplay = POINTER(c_int)
_GtkWidgetPath = POINTER(c_int)
_GdkScreen = POINTER(c_int)
_PangoFontMetrics = POINTER(c_int)
_GdkVisual = POINTER(c_int)
_PangoFontMap = POINTER(c_int)
_GSList = POINTER(c_int)
_WebKitWebFrame = POINTER(c_int)
_JSString = POINTER(c_int)
_GtkWidget = POINTER(c_int)
__WebKitNetworkRequest = POINTER(c_int)
__GdkWindow = POINTER(c_int)
__PangoFontFamily = POINTER(c_int)
__JSContextGroup = POINTER(c_int)
__GPollFD = POINTER(c_int)
__cairo_region_t = POINTER(c_int)
_PangoFontset = POINTER(c_int)
_GdkWindow = POINTER(c_int)
__PangoFontDescription = POINTER(c_int)
__GtkBorder = POINTER(c_int)
__GError = POINTER(c_int)
__PangoCoverage = POINTER(c_int)
_WebKitViewportAttributes = POINTER(c_int)
_JSClass = POINTER(c_int)
_WebKitWebHistoryItem = POINTER(c_int)
__cairo_t = POINTER(c_int)
__GWeakRef = POINTER(c_int)
__GdkVisual = POINTER(c_int)
__GdkEventButton = POINTER(c_int)
_GdkDevice = POINTER(c_int)
__PangoRectangle = POINTER(c_int)
__GtkAccelGroup = POINTER(c_int)
_GObject = POINTER(c_int)
__GtkIconSource = POINTER(c_int)
__JSContext = POINTER(c_int)
_PangoFontsetSimple = POINTER(c_int)
__GtkAllocation = POINTER(c_int)
__GtkWidget = POINTER(c_int)
_PangoLayoutLine = POINTER(c_int)
__GtkIconSet = POINTER(c_int)
_WebKitWebView = POINTER(c_int)
__PangoTabArray = POINTER(c_int)
_WebKitHitTestResult = POINTER(c_int)
__GValue = POINTER(c_int)
_GdkDeviceManager = POINTER(c_int)
_GdkCursor = POINTER(c_int)
_WebKitDOMDocument = POINTER(c_int)
__PangoMatrix = POINTER(c_int)
__GtkPrintOperation = POINTER(c_int)
_PangoContext = POINTER(c_int)
__GList = POINTER(c_int)
__WebKitWebView = POINTER(c_int)
_WebKitWebWindowFeatures = POINTER(c_int)
_PangoCoverage = POINTER(c_int)
_GParamSpec = POINTER(c_int)
_GList = POINTER(c_int)
__GdkRGBA = POINTER(c_int)
__GTimeVal = POINTER(c_int)
__GSourceFuncs = POINTER(c_int)
__JSPropertyNameAccumulator = POINTER(c_int)
__PangoGlyphString = POINTER(c_int)
__JSGlobalContext = POINTER(c_int)
_WebKitSecurityOrigin = POINTER(c_int)
__GObjectClass = POINTER(c_int)
__GSList = POINTER(c_int)
_PangoAnalysis = POINTER(c_int)
__GdkWindowAttr = POINTER(c_int)
_SoupMessage = POINTER(c_int)
_WebKitWebDataSource = POINTER(c_int)
__GdkColor = POINTER(c_int)
_JSContextGroup = POINTER(c_int)
__GdkRectangle = POINTER(c_int)
__PangoLanguage = POINTER(c_int)
_PangoAttrList = POINTER(c_int)
__gunichar = POINTER(c_int)
__GdkWMDecoration = POINTER(c_int)
__PangoLogAttr = POINTER(c_int)
_PangoLayout = POINTER(c_int)
_JSPropertyNameArray = POINTER(c_int)
__JSObject = POINTER(c_int)
_WebKitWebNavigationAction = POINTER(c_int)
_GtkStyle = POINTER(c_int)
__GParameter = POINTER(c_int)
__GtkStyle = POINTER(c_int)
__GIcon = POINTER(c_int)
__GtkWindow = POINTER(c_int)
_PangoLayoutRun = POINTER(c_int)
__cairo_pattern_t = POINTER(c_int)
__GdkPixbuf = POINTER(c_int)
_WebKitGeolocationPolicyDecision = POINTER(c_int)
_GtkSettings = POINTER(c_int)
__GSourceCallbackFuncs = POINTER(c_int)
__GtkTargetEntry = POINTER(c_int)
__GtkApplication = POINTER(c_int)
_GtkClipboard = POINTER(c_int)
_GByteArray = POINTER(c_int)
__GdkScreen = POINTER(c_int)
_PangoLanguage = POINTER(c_int)
__GdkDevice = POINTER(c_int)
_PangoTabArray = POINTER(c_int)
"""Enumerations"""
PangoStyle = c_int
PangoWeight = c_int
PangoVariant = c_int
PangoStretch = c_int
PangoFontMask = c_int
GtkWidgetHelpType = c_int
GtkTextDirection = c_int
GtkSizeRequestMode = c_int
GtkAlign = c_int
GdkPixbufError = c_int
GdkColorspace = c_int
GdkPixbufAlphaMode = c_int
GtkIconSize = c_int
GdkWindowType = c_int
GdkWindowWindowClass = c_int
GdkWindowHints = c_int
GdkGravity = c_int
GdkWindowEdgeh = c_int
GdkWindowTypeHint = c_int
GdkWindowAttributesType = c_int
GdkFilterReturn = c_int
GdkModifierType = c_int
GdkWMDecoration = c_int
GdkWMFunction = c_int
GdkInputSource = c_int
GdkInputMode = c_int
GdkAxisUse = c_int
GdkDeviceType = c_int
GdkGrabOwnership = c_int
GdkCursorType = c_int
GdkVisualType = c_int
GdkByteOrder = c_int
GtkRcFlags = c_int
GtkRcTokenType = c_int
PangoWrapMode = c_int
PangoEllipsizeMode = c_int
PangoAlignment = c_int
WebKitLoadStatus = c_int
WebKitNavigationResponse = c_int
WebKitWebViewTargetInfo = c_int
WebKitWebViewViewMode = c_int
WebKitEditingBehavior = c_int
GdkInputSource = c_int
GdkInputMode = c_int
GdkAxisUse = c_int
GdkDeviceType = c_int
GdkGrabOwnership = c_int
GtkDialogFlags = c_int
GtkResponseType = c_int
WebKitWebNavigationReason = c_int
PangoWrapMode = c_int
PangoEllipsizeMode = c_int
PangoAlignment = c_int

import gobject__GObject
class GSource( gobject__GObject.GObject):
    """Class GSource Constructors"""
    def __init__( self, struct_size,  obj = None):
        if obj: self._object = obj
        else:
            libgobject.g_source_new.restype = POINTER(c_int)
            
            libgobject.g_source_new.argtypes = [guint]
            self._object = libgobject.g_source_new(struct_size, )

    """Methods"""
    def remove_poll(  self, fd, ):
        if fd: fd = fd._object
        else: fd = POINTER(c_int)()

        libgobject.g_source_remove_poll.argtypes = [_GSource,_GPollFD]
        
        libgobject.g_source_remove_poll( self._object,fd )

    def set_callback_indirect(  self, callback_data, callback_funcs, ):
        if callback_funcs: callback_funcs = callback_funcs._object
        else: callback_funcs = POINTER(c_int)()

        libgobject.g_source_set_callback_indirect.argtypes = [_GSource,gpointer,_GSourceCallbackFuncs]
        
        libgobject.g_source_set_callback_indirect( self._object,callback_data,callback_funcs )

    def destroy(  self, ):

        libgobject.g_source_destroy.argtypes = [_GSource]
        
        libgobject.g_source_destroy( self._object )

    def get_id(  self, ):

        libgobject.g_source_get_id.restype = guint
        libgobject.g_source_get_id.argtypes = [_GSource]
        
        return libgobject.g_source_get_id( self._object )

    def get_context(  self, ):

        libgobject.g_source_get_context.restype = _GMainContext
        libgobject.g_source_get_context.argtypes = [_GSource]
        from gobject import GMainContext
        return GMainContext(None,None, obj=libgobject.g_source_get_context( self._object ) or POINTER(c_int)())

    def set_can_recurse(  self, can_recurse, ):

        libgobject.g_source_set_can_recurse.argtypes = [_GSource,gboolean]
        
        libgobject.g_source_set_can_recurse( self._object,can_recurse )

    def get_name(  self, ):

        libgobject.g_source_get_name.restype = c_char_p
        libgobject.g_source_get_name.argtypes = [_GSource]
        
        return libgobject.g_source_get_name( self._object )

    def get_priority(  self, ):

        libgobject.g_source_get_priority.restype = gint
        libgobject.g_source_get_priority.argtypes = [_GSource]
        
        return libgobject.g_source_get_priority( self._object )

    def ref(  self, ):

        libgobject.g_source_ref.restype = _GSource
        libgobject.g_source_ref.argtypes = [_GSource]
        from gobject import GSource
        return GSource( obj=libgobject.g_source_ref( self._object ) or POINTER(c_int)())

    def remove_child_source(  self, child_source, ):
        if child_source: child_source = child_source._object
        else: child_source = POINTER(c_int)()

        libgobject.g_source_remove_child_source.argtypes = [_GSource,_GSource]
        
        libgobject.g_source_remove_child_source( self._object,child_source )

    def add_child_source(  self, child_source, ):
        if child_source: child_source = child_source._object
        else: child_source = POINTER(c_int)()

        libgobject.g_source_add_child_source.argtypes = [_GSource,_GSource]
        
        libgobject.g_source_add_child_source( self._object,child_source )

    def set_name(  self, name, ):

        libgobject.g_source_set_name.argtypes = [_GSource,c_char_p]
        
        libgobject.g_source_set_name( self._object,name )

    def get_can_recurse(  self, ):

        libgobject.g_source_get_can_recurse.restype = gboolean
        libgobject.g_source_get_can_recurse.argtypes = [_GSource]
        
        return libgobject.g_source_get_can_recurse( self._object )

    def get_current_time(  self, timeval, ):
        if timeval: timeval = timeval._object
        else: timeval = POINTER(c_int)()

        libgobject.g_source_get_current_time.argtypes = [_GSource,_GTimeVal]
        
        libgobject.g_source_get_current_time( self._object,timeval )

    def is_destroyed(  self, ):

        libgobject.g_source_is_destroyed.restype = gboolean
        libgobject.g_source_is_destroyed.argtypes = [_GSource]
        
        return libgobject.g_source_is_destroyed( self._object )

    def unref(  self, ):

        libgobject.g_source_unref.argtypes = [_GSource]
        
        libgobject.g_source_unref( self._object )

    def add_poll(  self, fd, ):
        if fd: fd = fd._object
        else: fd = POINTER(c_int)()

        libgobject.g_source_add_poll.argtypes = [_GSource,_GPollFD]
        
        libgobject.g_source_add_poll( self._object,fd )

    def set_priority(  self, priority, ):

        libgobject.g_source_set_priority.argtypes = [_GSource,gint]
        
        libgobject.g_source_set_priority( self._object,priority )

    def set_funcs(  self, funcs, ):
        if funcs: funcs = funcs._object
        else: funcs = POINTER(c_int)()

        libgobject.g_source_set_funcs.argtypes = [_GSource,_GSourceFuncs]
        
        libgobject.g_source_set_funcs( self._object,funcs )

    def get_time(  self, ):

        libgobject.g_source_get_time.restype = gint64
        libgobject.g_source_get_time.argtypes = [_GSource]
        
        return libgobject.g_source_get_time( self._object )

    def set_name_by_id(  self, tag, name, ):

        libgobject.g_source_set_name_by_id.argtypes = [_GSource,guint,c_char_p]
        
        libgobject.g_source_set_name_by_id( self._object,tag,name )

    def set_callback(  self, func, data, notify, ):

        libgobject.g_source_set_callback.argtypes = [_GSource,GSourceFunc,gpointer,GDestroyNotify]
        
        libgobject.g_source_set_callback( self._object,func,data,notify )

    def attach(  self, context, ):
        if context: context = context._object
        else: context = POINTER(c_int)()

        libgobject.g_source_attach.restype = guint
        libgobject.g_source_attach.argtypes = [_GSource,_GMainContext]
        
        return libgobject.g_source_attach( self._object,context )

    @staticmethod
    def remove_by_user_data( user_data,):
        libgobject.g_source_remove_by_user_data.restype = gboolean
        libgobject.g_source_remove_by_user_data.argtypes = [gpointer]
        
        return     libgobject.g_source_remove_by_user_data(user_data, )

    @staticmethod
    def remove( tag,):
        libgobject.g_source_remove.restype = gboolean
        libgobject.g_source_remove.argtypes = [guint]
        
        return     libgobject.g_source_remove(tag, )

    @staticmethod
    def remove_by_funcs_user_data( funcs, user_data,):
        if funcs: funcs = funcs._object
        else: funcs = POINTER(c_int)()
        libgobject.g_source_remove_by_funcs_user_data.restype = gboolean
        libgobject.g_source_remove_by_funcs_user_data.argtypes = [_GSourceFuncs,gpointer]
        
        return     libgobject.g_source_remove_by_funcs_user_data(funcs, user_data, )

