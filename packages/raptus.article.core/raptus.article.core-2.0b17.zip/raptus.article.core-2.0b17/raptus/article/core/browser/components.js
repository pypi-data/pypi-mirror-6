var raptus_article = {
  components_selector: '#components li',
  showhide_selector: '.manage a[href*="article_showhideitem"]',
  manage_selector: '.article-manage .manage-components',
  toggle_selector: '.article-toggle',
  dragndrop_selector: 'ul.listing:has(> li.component > .manage a[href*="article_moveitem"]), ' +
                      'ul.gallery:has(> li.component > .manage a[href*="article_moveitem"]), ' +
                      'div.tables:has(> div.component > .manage a[href*="article_moveitem"]), ' +
                      'table.table > tbody:has(.manage a[href*="article_moveitem"]), ' +
                      'div.allcontent:has(> div.article > .manage a[href*="article_moveitem"])'
};

(function($) {

  var changed = false;
  var bound = false;

  raptus_article.init = function(container) {
    container.find(raptus_article.components_selector).each(raptus_article.init_components);
    container.find(raptus_article.showhide_selector).each(raptus_article.init_showhide);
    container.find(raptus_article.manage_selector).each(raptus_article.init_manage);
    container.find(raptus_article.toggle_selector).each(raptus_article.init_toggle);
    container.find(raptus_article.dragndrop_selector).each(raptus_article.init_dragndrop);
    if(!bound)
      $(window).unbind('unload').bind('unload,', raptus_article.confirm)
               .unbind('beforeunload').bind('beforeunload', function() {
                 if(changed)
                   return $('.article-toggle').data('confirm');
               });
    bound = true;
  };

  raptus_article.confirm = function(e) {
    if(changed && !window.confirm($('.article-toggle').data('confirm')))
      return false;
  }

  raptus_article.init_components = function() {
    var li = $(this);
    var label = li.find('label');
    var img = li.find('img');
    var span = li.find('span');
    jQuery('<span class="information clearfix"></span>').appendTo(label);
    var info = label.find('.information');
    img.appendTo(info);
    span.appendTo(info);
    li.hover(
      function() {
        $(this).addClass('hover');
      },
      function() {
        $(this).removeClass('hover');
      });
  };

  raptus_article.init_showhide = function() {
    var link = $(this);
    var img = link.find('img');
    var component = link.closest('.component');
    var locked = false;
    link.click(function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      if(locked)
        return;
      locked = true;
      var href = link.attr('href');
      $.get(href, {'ajax_load': 1}, function(data) {
        if(data == '0') {
          locked = false;
          return;
        }
        if(href.match(/action=hide/)) {
          link.attr('href', href.replace('action=hide', 'action=show'));
          img.attr('src', img.attr('src').replace('hide.png', 'show.png'));
          component.addClass('hidden');
        } else {
          link.attr('href', href.replace('action=show', 'action=hide'));
          img.attr('src', img.attr('src').replace('show.png', 'hide.png'));
          component.removeClass('hidden');
        }
        locked = false;
      });
    });
  };

  raptus_article.init_manage = function() {
    var link = $(this);
    var container = link.closest('.article-manage');
    var href = link.attr('href');
    var components = false;
    var manager = container.closest('.viewletmanager');
    var form = false;
    var locked = false;
    var close = false;
    var timer = false;
    function reload(e) {
      changed = true;
      if(timer)
        window.clearTimeout(timer);
      timer = window.setTimeout(function() {
        raptus_article.update_manager(manager);
        timer = false;
      }, 500);
    }
    link.click(function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      if(!components && !locked) {
        locked = true;
        link.addClass('loading');
        $.get(href, {'ajax_load': 1}, function(data) {
          components = $('<div />').append(data.split(/<body[^>]+>/)[1].split(/<\/body>/)[0].replace(/<script[^>]*>[^<]*<\/script[^>]*>/, ''))
                                   .find('form#components')
                                   .wrap('<div class="components" />')
                                   .closest('.components')
                                   .hide()
                                   .appendTo(container);
          close = $('<a href="javascript://" class="close">✕</a>').prependTo(components).click(function(e) {
            link.trigger('click');
          });
          form = components.find('form');
          form.find('.actionButtons').remove();
          form.find('input[type="checkbox"]').attr('name', 'components').change(reload);
          form.find('label').click(reload);
          raptus_article.init(components);
          link.removeClass('loading');
          locked = false;
          link.trigger('click');
        });
        return;
      }
      if(container.hasClass('open'))
        components.stop().slideUp('fast');
      else
        components.stop().removeAttr('style').hide().slideDown('fast');
      container.toggleClass('open');
    });
  };

  raptus_article.update_manager = function(manager) {
    var form = manager.find('.components > form');
    var toggle = manager.find('> .article-manage .manage-components');
    var viewlets = manager.find('> .viewlets');
    if(form.size())
      var data = form.serializeArray();
    else
      var data = [{
        'name': 'actual',
        'value': 1
      }]
    manager.addClass('loading');
    manager.data('current_xhr', $.get(toggle.attr('href').replace('@@components', '@@viewlet.manager'), data, function(data, status, xhr) {
      if(xhr !== manager.data('current_xhr'))
        return;
      var data = $('<div />').append(data).find('.viewletmanager > .viewlets');
      if(data.size())
        viewlets.html(data.html());
      raptus_article.init(viewlets);
      manager.trigger('viewlets.updated');
      manager.removeClass('loading');
    }));
  }

  raptus_article.init_toggle = function() {
    var toggle = $(this);
    $(window).scroll(function(e) {
      var top = $(window).scrollTop();
      if(top + 10 > toggle_offset.top)
        toggle.css({
          'position': 'fixed',
          'left': toggle_offset.left,
          'width': toggle_width,
          'top': '10px',
          'z-index': 10
        });
      else
        toggle.removeAttr('style');
    });
    var view = toggle.find('.view').hide();
    var save = toggle.find('.save').removeClass('hiddenStructure');
    var cancel = toggle.find('.cancel').removeClass('hiddenStructure');
    var toggle_offset = toggle.offset();
    var toggle_width = toggle.width();
    if(!view.size())
      return;
    save.click(function(e) {
      e.preventDefault();
      e.stopImmediatePropagation();
      save.addClass('loading');
      raptus_article.save_components(function() {
        document.location = view.attr('href');
      });
    });
    cancel.click(function(e) {
      changed = false;
    });
  };

  raptus_article.save_components = function(callback) {
    $('.viewletmanager .components form').each(function() {
      var form = $(this);
      form.find('input[type="checkbox"]').attr('name', 'form.components:list');
      var data = form.serializeArray();
      data.push({
        'name': 'form.submitted',
        'value': 1
      });
      data.push({
        'name': 'ajax_load',
        'value': 1
      });
      $.ajax(form.attr('action'), {
        data: data,
        type: 'POST',
        async: false
      });
    });
    changed = false;
    callback();
  }

  raptus_article.init_dragndrop = function() {
    if(!$.fn.sortable)
      return;
    var container = $(this);
    var mng = '> .manage';
    if(container.is('div.allcontent'))
      var itm = '> div.article';
    else if(container.is('div.tables'))
      var itm = '> div.component';
    else if(container.is('table.table > tbody')) {
      var itm = '> tr:not(.add-row)';
      var mng = '> td:last-child > .manage';
    } else
      var itm = '> li.component';
    var columns = container.find(itm + '.last:first').index() + 1;
    container.find(itm + ' ' + mng + ' a[href*="article_moveitem"]').hide();
    container.find(itm + ' ' + mng).prepend('<a class="move">░</a>');
    function update_classes() {
      var items = container.find(itm + ':not(.ui-sortable-helper)').removeClass('odd even first last');
      var l = columns;
      var i = 0;
      items.each(function() {
        var item = $(this);
        var ci = i++ % columns;
        if(ci == 0)
            item.addClass('first')
        if(ci == l-1)
            item.addClass('last')
        if(ci % 2 == 0)
            item.addClass('odd')
        if(ci % 2 == 1)
            item.addClass('even')
      });
    }
    container.sortable({
      items: itm,
      handle: mng + ' a.move',
      start: function(e, ui) {
        ui.item.data('pos', ui.item.index());
      },
      change: function(e, ui) {
        update_classes();
      },
      update: function(e, ui) {
        update_classes();
        var target = false;
        var id = ui.item.find(mng).data('id');
        if(ui.item.index() > ui.item.data('pos'))
          var target = ui.item.prev();
        else if(ui.item.index() < ui.item.data('pos'))
          var target = ui.item.next();
        if(target) {
          $.get(ui.item.find(mng + ' a[href*="article_moveitem"]').attr('href').split('?')[0].replace('article_moveitem', '@@article_move'), {
            item: id,
            target: target.find(mng).data('id')
          }, function(data) {
            var updated = [];
            $('.manage[data-id="' + id + '"]').each(function() {
              var item = $(this).parent();
              if(item.get(0) == ui.item.get(0))
                return;
              var manager = item.closest('.viewletmanager');
              var mid = manager.data('id');
              if(mid in updated)
                return;
              raptus_article.update_manager(manager);
              updated.push(mid);
            });
          });
        }
      }
    });
  };

  $(document).ready(function() {
    raptus_article.init($('body'));
  });

})(jQuery);
