// A quick video widget that incorporates VideoJS library
// For use in The Secret World's tutorial system revamp
// Leigh Johnson 2/10/2015 
// http://leighjohnson.me
// http://github.com/Nuwen

CKEDITOR.plugins.add('widget_video', {
    requires: 'widget',
    icons: 'widget_video',
    inline: true,
    init: function(editor) {
    	// register widget with editor instance
    	editor.widget.add('widget_video', {
    		button: 'Add a video'
    	});
    }
});