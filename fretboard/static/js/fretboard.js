var $main = $('#content'),
    main_height   = $main.outerHeight(),
    $forum_search = $('#forum_search'),
    $img_field    = $('#id_image').closest('p');

// extract query parameters by name. Used for local storage
function urlParams(name){
  var results = new RegExp('[\\?&]' + name + '=([^&#]*)').exec(window.location.href);
  if (!results) {
    return 0;
  }
  return results[1] || 0;
}


$img_field.hide().addClass('breakout');

// Hide/show forum search
$forum_search.hide();
$('#search-box-trigger').click(function(e){
    e.preventDefault();
    $forum_search.slideToggle();
});


// Confirm toxic topic clicks. 
// Note: toxic post clicks are handled side-wide by the comment-list handler.
// Toxic post toggle
$('#topic_list article.toxic').click(function(e) {
  if (!confirm('Are you sure you want to see this? It could get ugly.')) {
    e.preventDefault();
  }
});
$('form.toxic input[type=submit]').click(function(e) {
  if (!confirm('Are you really sure you want to contribute to this mess?')) {
    e.preventDefault();
    $(this).closest('form').find('textarea').val('');
  }
});


// INIT markitup
$("#reply #id_text").markItUp(gp_markdown_settings);

// Admin/moderation links
$('.tool_trigger').click(function() {
    $(this).hide();
    $(this).parent().find('.post-admin').show();
});

// localstorage of topics/views
if (Modernizr.localstorage && lscache) {
  var new_topic = urlParams('new_topic');
  var new_post  = urlParams('new_post');
  var topics    = lscache.get('topics');

  // make sure topics and viewed exist in lscache
  if (!topics) {
      topics = [];
  }
  if (new_topic && new_topic !== null && $.inArray(new_topic, topics) === -1) {
    topics.push(new_topic); // new topics
  }
  if (new_post && new_post !== null && $.inArray(new_post, topics) === -1) {
    topics.push(new_post); // new posts
  }
  if (topics.length > 201){
    topics.splice(0,1);
  }

  if (topics !== null) {
    lscache.set('topics', topics);
    var $topics_link = $('#commented_topics a');
    if($topics_link.length) {
      $topics_link.prepend('<span class="left counter">'+ topics.length + '</span>');
      $topics_link[0].search += ('?topics=' + topics);
    }
  }
}

// Dropdown avatars
$("#comment-list .avatar-hold a").each(function() {
  var appended = false;
  var $container = $(this).parent();
  $(this).click(function(e) {
    e.preventDefault();
    if (appended === false) {
      $.getJSON(this.href, function(data) {
        var results = '<ul class="profile_preview fancy"><li>' + data.name + '</li>' +
           '<li><strong>Joined:</strong> '+ data.joined +'</li>';
        if (data.location) {
          results += "<li><strong>Location:</strong> " + data.location +'</li>';
        }
        if (data.website) {
          results += '<li><a href="' + data.website +'">Web Site</a></li>';
        }
        results += '<li><a href="' + data.contact_url + '">Contact</a></li>' +
          '<li><a href="' + data.profile_url + '">View Full Profile</a></li></ul>';
        $container.append(results);
        appended = true;
      });
    } else {
      $container.find('ul.profile_preview').toggle();
    }
  });
});

// pop-in place reply box
$("ul.postcontrols li a[href=#reply]").click(function(e){
  e.preventDefault();
  $(this).closest('footer').append($('#reply').slideDown('fast'));
});

$('#reply').on('click touchend', 'li.icon-photo', function(e) {
  $img_field.toggle();
});

// helper function for infinite scrollers 
// updates vars post-load

function updatePostLoad(url, newHash) {
  loadable=true;
  main_height = $main.outerHeight();
  if (typeof(_gaq) != 'undefined'){
    _gaq.push(['_trackPageview']);
  }
  //if (Modernizr.history) {
  //  history.pushState(null, null, url);
  //}
}

function load_topics() {
  var url        = window.location.pathname + '?page=' + page,
      $topicList = $('#topic_list');
      newHash    = 'page- '+ page;

  $.get(url, function(data) {
    $topicList.append('<h1 id="#'+ newHash +'">Page '+ page + '</h1>' + data);
    updatePostLoad(url, newHash);
  });
}

function load_posts() {
  var url          = topic_short_url + page +'/',
      $commentList = $('#comment-list'),
      newHash    = 'page- '+ page;

  $.get(url, function(data) {
    $commentList.append('<h1 id="#'+ newHash +'">Page '+ page + '</h1>' + data);
    load_images();
    current_page.html(original_page + '-' +page);  // adjust pagination
    loaded.push(page);
    updatePostLoad(url);
  });
}

// check for loading of new content.
if (typeof loadable != 'undefined' && loadable === true) {
  var didScroll = false;

  $(window).scroll(function() {
    didScroll = true;
  });

  setInterval(function() {
    if ( didScroll ) {
      didScroll = false;
      main_offset = getYOffset();
      if (main_offset > (main_height * 0.75) && loadable === true && page <= page_max) {
        loadable=false;
        page += 1;
        if (typeof topiclist != 'undefined') {
          load_topics();
        }
        if (typeof postlist != 'undefined' && $.inArray(page+1, loaded) === -1) {
          load_posts();
        }
      }
    }
  }, 250);
}
