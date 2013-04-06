
/**
 * Namespace.
 */
var tb = {}

/**
 * Constructor.
 */
tb.Game = function() {};


$(document).ready(function(){

  var game = new tb.Game();

  window.forbiddenWords = [];


  $('#session-word').change(function() {
    window.forbiddenWords =
    $(this).next().text($(this).find(":selected").data('forbidden_words'));
  });
});