/**
 * pu.in content library. This library takes care of frontend content
 * editing.
 * This JS enables inline add, remove and edit.
 *
 * Inline add
 * ----------
 * Add class 'add-inline' to your link tag.
 *
 */

// pu_in namespace
if (pu_in == undefined) {
  var pu_in = {};
}

// Our own namespace
pu_in['content'] = {};


/**
 * Remove the element that is the '.editable' parent of the event's
 * target.
 */
pu_in.content.remove_inline = function(tgt) {

  $.post(tgt.attr("href"), {},
         function(data, status, xhr) {

           var dict = pu_in.core.requestAsDataDict(data, status, xhr);

           if (pu_in.core.checkStatus(xhr) < 0) {
             pu_in.core.showMessage(dict['errors'], "error");
           } else {
             pu_in.core.handleCallback(tgt);
             tgt.parents(".editable").eq(0).remove();
           }
         },
         "json");
};


/**
 * Edit inline. If the href is a link to an id, show that id (assuming
 * it is the edit form), else fetch the link and show that in the
 * modal box.
 * @param tgt Target link.
 */
pu_in.content.edit_inline = function(tgt) {

  var target = null;
  var defaults = {};
  var datatype = tgt.data("pu_datatype") || "text";

  if (tgt.attr("target")) {
    target = $(tgt.attr("target"));
  } else {
    target = tgt.parents(".editable").eq(0);
    defaults['pu_targetbehavior'] = 'replace';
  }

  if (tgt.attr("href").startsWith("#")) {
    $(tgt.attr("href")).show();
  } else {
    $.get(tgt.attr("href"), function(data, status, xhr) {

        var dict = pu_in.core.requestAsDataDict(data, status, xhr);

        $(pu_in.settings.modal_id + " .modal-body").html(dict['html']);

        $(document).triggerHandler("pu_in_content_load_modal", 
                                   [$(pu_in.settings.modal_id)]);

        // Bind submit
        $(pu_in.settings.modal_id).on("submit.pu_in_content", "form", function(e) {

            var form = $(e.target);

            $.post(form.attr("action"),
                   form.serialize(),
                   function(data, status, xhr) {

                     var dict = pu_in.core.requestAsDataDict(data, status, xhr);

                     if (pu_in.core.checkStatus(xhr) < 0) {
                       $(pu_in.settings.modal_id + " .modal-body").html(dict['html']);
                       $(document).triggerHandler("pu_in_content_load_modal", 
                                                  [$(pu_in.settings.modal_id)]);
                     } else {
                       pu_in.core.handleResult(tgt, target, data, status, xhr, 
                                               defaults);
                       $(pu_in.settings.modal_id).modal('hide'); 
                     }
                   }, datatype);

            e.preventDefault();
            e.stopPropagation();
          });

        $(pu_in.settings.modal_id).modal();
      }, datatype);
  }
};


/**
 * Add inline. This involves either showing an existing add form, or
 * fetching it from remote.
 * @param tgt Target link.
 */
pu_in.content.add_inline = function(tgt) {

  var target = tgt.attr("target") ? $(tgt.attr("target")) : null;
  var defaults = {'pu_targetbehavior': 'append'};
  var datatype = tgt.data("pu_datatype") || "text";

  if (tgt.attr("href").startsWith("#")) {
    $(tgt.attr("href")).show();
  } else {
    $.get(tgt.attr("href"), function(data, status, xhr) {

        var dict = pu_in.core.requestAsDataDict(data, status, xhr);
        
        $(pu_in.settings.modal_id + " .modal-body").html(dict['html']);
        $(document).triggerHandler("pu_in_content_load_modal", 
                                   [$(pu_in.settings.modal_id)]);

        $(pu_in.settings.modal_id).on("submit.pu_in_content", "form", function(e) {

            var form = $(e.target);

            $.post(form.attr("action"),
                   form.serialize(),
                   function(data, status, xhr) {

                     var dict = pu_in.core.requestAsDataDict(data, status, xhr);
                     
                     if (pu_in.core.checkStatus(xhr) < 0) {
                       $(pu_in.settings.modal_id + " .modal-body").html(dict['html']);
                       $(document).triggerHandler("pu_in_content_load_modal", 
                                                  [$(pu_in.settings.modal_id)]);
                     } else {
                       pu_in.core.handleResult(tgt, target, data, status, xhr, 
                                               defaults);
                       $(pu_in.settings.modal_id).modal('hide');
                     }
                   }, datatype);

            e.preventDefault();
            e.stopPropagation();

          });
        $(pu_in.settings.modal_id).modal('show');        
      }, datatype);
  }
}


/**
 * Handle submission of the add form. Rebind submit to self.
 * @param form Form to submit
 * @param add_to Element to add result to
 */
pu_in.content._handle_add_submit = function(link, form, add_to) {

  return false;
};


// Initialize pu_in.content
//
$(document).ready(function() {

    $(document).on("click", ".rm-inline", function(event) {

        var tgt = $(event.currentTarget);

        if (!tgt.hasClass("disabled")) {
          if (tgt.data("pu_confirmdelete")) {
            pu_in.core.confirmMessage("Weet je zeker dat je dit item wilt verwijderen?",
                                      
                                      pu_in.content.remove_inline, [tgt]);
          } else {
            pu_in.content.remove_inline(tgt);
          }
        }

        event.preventDefault();        
      });

    $(document).on("click", ".edit-inline", function(event) {

        event.preventDefault();

        var tgt = $(event.currentTarget);

        console.log(tgt.attr("class"));

        if (!tgt.hasClass("disabled")) {
          pu_in.content.edit_inline(tgt);
        }
      });

    $(document).on("click", ".add-inline", function(event) {

        var tgt = $(event.target);

        if (!tgt.hasClass("add-inline")) {
          tgt = tgt.parents(".add-inline");
        }

        if (!tgt.hasClass("disabled")) {
          pu_in.content.add_inline(tgt);
        }

        event.preventDefault();
      });

    // Clean up bind after use
    $(pu_in.settings.modal_id).on('hide', function () {
        $(pu_in.settings.modal_id).off("submit.pu_in_content");
      });
  });
