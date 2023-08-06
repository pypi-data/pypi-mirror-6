jQuery(function($) {
  if ($('#content-views #contentview-local-mls-config').length > 0) {
    // Show the local MLS settings form with a nice overlay.
    $('#content-views #contentview-local-mls-config > a').prepOverlay({
      subtype: 'ajax',
      filter: '#content>*',
      formselector: '#content-core > form',
      noform: 'reload',
      closeselector: '[name="form.buttons.cancel"]'
    });
  }
});
