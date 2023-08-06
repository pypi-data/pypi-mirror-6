(function($) {

  function init(e) {
    var container = $(this);
    var images = new Array();
    container.find('a[rel^="inlinelightbox"]').each(function() {
      var o = $(this);
      var rel = o.attr('rel');
      if($.inArray(rel, images) == -1)
        images.push(rel);
    });
    for(var i=0; i<images.length; i++)
      container.find('a[rel="'+images[i]+'"]').inlineLightBox(inlinelightbox.settings['standard']);
  }

  $(document).ready(function(e) {
    $.proxy(init, $('body'))(e);
    $('.viewletmanager').bind('viewlets.updated', init);
  });

})(jQuery);
