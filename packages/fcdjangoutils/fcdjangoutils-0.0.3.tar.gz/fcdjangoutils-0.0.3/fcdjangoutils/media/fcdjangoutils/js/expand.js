expand = {};

expand.prepare = function () {
  //$('.autohide-body').hide();
  $('.autohide-button:not(.autohide-init)').addClass('autohide-init').click(function () {
    var id = this.id.replace(new RegExp("-button$"), "");
    $(this).toggleClass('autohide-expanded');
    $('#' + id + '-body').toggle(500, function() {
      $('.new_comment', this).focus();
    });
  });

  $('.new_comment:not(.new-comment-init)').addClass('new-comment-init').focus(function() {
      var comment = $(this);
      comment.addClass('expanded', 200);
      comment.parent().next('button.submit_comment').show();
    });
};

$(document).ready(expand.prepare);
