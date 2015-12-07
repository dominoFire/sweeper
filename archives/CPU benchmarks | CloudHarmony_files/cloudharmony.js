//   Custom select
var __dcid;
function customSelect(select) {
  if (select && select == 'undefined') select = null;
  
  $(select ? select : ".select").each(function() {
    if (select || $(this).next('.custom-select').length == 0) {
      $(this).next('.custom-select').remove();
      $('<div class="custom-select"><div class="inner"><span class="text"></span><i class="icon_select_arrow"></i></div><div class="drop-list"></div>').insertAfter(this);

      $(this).next('.custom-select').each(function() {
        var selectClass = $(this).prev('.select').attr('class');  
        $(this).addClass(selectClass).removeClass('select');
      });
      
      var vals = {};
      $(this).find("option").each( function() {
        vals[$(this).val()] = $(this).html();
        if ($(this).attr('data-recomend')) vals[$(this).val()] += '<i class="icon-recomended"></i>';
      });
      
      var optList = $(this).next('.custom-select').find('div.drop-list');
      
      $.each(vals, function(key, label) {
        var div = $('<div/>')
          .addClass('option')
          .html(label)
          .attr('data-value', key)
          .appendTo(optList);  
      });
      
      $(this).next('.custom-select').each(function() {
        var selected = $(this).prev('select').find('option:selected').index();
        $(this).find('.option').eq(selected).addClass('selected');  
        var optionVal = $(this).find('.selected').html();
        $(this).find('.text').html(optionVal);
      });
      
      $(this).next('.custom-select').find('.drop-list .option').click(function() {
        $(this).siblings('.option').removeClass('selected');    
        $(this).addClass('selected');
        var optionVal = $(this).html();
        $(this).closest('.custom-select').find('.text').html(optionVal);  

        var curIn = $(this).index();
        $(this).closest('.custom-select').prev('select').find('option').eq(curIn).prop("selected",true);
        $(this).closest('.custom-select').prev('select').change();
      });
      
      $(this).next('.custom-select').click(function() {
        if ($(this).hasClass('disabled')) {
          return false;
        } else {
          if($(this).find('.drop-list').is('.open')){
            $('.custom-select').find('.drop-list').removeClass('open');    
          } else {
            $('.custom-select').find('.drop-list').removeClass('open');
            $(this).find('.drop-list').addClass('open');    
          }
        }
      });
    }
  });
  
  if (!select) {
    $(document).click(function(e){
      var target = $(e.target);
      if (target.is('.custom-select') || target.parents('.custom-select').length) return;
      $('.custom-select .drop-list').removeClass('open');
    }); 
  }
}
 
 //Table striped 
function tableStriped(selector, hidden) {
  var tables = selector && typeof selector !== 'undefined' ? $(selector).find(".striped_wh") : $(".striped_wh");
  var v = hidden === true ? '' : ':visible';
  tables.each(function() {
    if ($(this).find('tbody').length) {
      $(this).find('tbody > tr:odd' + v + ' td, tbody > tr:odd' + v + ' th').css('background-color', '#F6F6F6');
      $(this).find('tbody > tr:even' + v + ' td, tbody > tr:even' + v + ' th').css('background-color', '#FFFFFF');
    }
    else {
      $(this).find('tr:odd' + v + ' td, tr:odd' + v + ' th').css('background-color', '#F6F6F6');
      $(this).find('tr:even' + v + ' td, tr:even' + v + ' th').css('background-color', '#FFFFFF'); 
    }
  });
  
  var tables = selector && typeof selector !== 'undefined' ? $(selector).find(".striped_gr") : $(".striped_gr");
  $(".striped_gr").each(function() {
    if ($(this).find('tbody').length) {
      $(this).find('tbody > tr' + v + ':even td, tbody > tr' + v + ':even th').css('background-color', '#F6F6F6');
      $(this).find('tbody > tr' + v + ':odd td, tbody > tr' + v + ':odd th').css('background-color', '#FFFFFF');
    }
    else {
      $(this).find('tr' + v + ':even td, tr' + v + ':even th').css('background-color', '#F6F6F6');
      $(this).find('tr' + v + ':odd td, tr' + v + ':odd th').css('background-color', '#FFFFFF'); 
    }
  });
}

//Modal windows
function modalWindow() {
  $(document).click(function(e){
    var target = $(e.target);
    if ((typeof forceModal !== 'undefined' && forceModal) || target.is('.modal, *[data-toggle=modal]') || target.parents('.modal').length) return;
    ch_close_modal();
  });

  $('body').on('click', '[data-toggle=modal]', function(e) {
    e.stopPropagation();
    e.preventDefault();
    $('.modal-backdrop').show();
    var top = $(window).scrollTop();
    var id = $(this).attr('data-id');
    if (typeof id == 'undefined') id = $(this).prop('href').split('#')[1];
    if (id.substring(0, 1) == '#') id = id.substring(1);
    var path = '[id="' + id + '"]';
    // console.log("Modal path is " + path + " with " + $(path).length + " elements");
    $(path).fadeIn(500).addClass('active');
    if ($(path).is('.full_width_modal')) {
      $(path).css( "top", top + 50 + 'px');
    } 
    else {
      $(path).css( "top", top + 115 + 'px');
    }
    $(path).find('.scroll_block').each(function() {
      $(this).tinyscrollbar_update();
      if ($(this).find('.scrollbar.disable').length > 0) {
        $(this).addClass('full');
      } 
      else {
        $(this).removeClass('full');
      }
    });   
  });

  $('.modal .modal_close').click(function(){
    ch_close_modal();
  });    

  $('.label span').click(function(){
    $(this).parent().fadeOut(300);
  }); 

  $('.ie8 .modal-backdrop').css('filter', 'alpha(opacity=70)');
}

// Dropdown
function dropdown() {
  if($(window).width() > 767) {
  $('.settings .dropdown > span').each(function() {
    var asidew = $(this).next('.dropdown_block').width();
    $(this).css('max-width', asidew - 27 + 'px');
  });

  $('body').on('mouseleave', '.dropdown' ,function(e){
     var timeout = setTimeout(function(){
       $('.dropdown_block').fadeOut(500,function() {
        $('.dropdown > span').removeClass('active');
        $(this).parent('.dropdown').removeClass('open');        
      });
     }, 1000);
     $('.dropdown, .ui-datepicker').mouseenter(function(){
      clearTimeout(timeout);
     });
   });    
  }

  $('body').on('click', '.dropdown > span', function() {  
    if ($(this).parent('.dropdown').hasClass('disabled')) {
      return false;
    } else {
      if ($(this).hasClass('active')) {  
        $(this).next('.dropdown_block').fadeOut(500,function() {
          $('.dropdown > span').removeClass('active');  
        });    
        $(this).parent('.dropdown').removeClass('open');      
      }  else {
        $('.dropdown > span, .help > span').removeClass('active');
        $('.block-help, .dropdown_block').fadeOut(500)
        $(this).addClass('active');
        $(this).next('.dropdown_block').fadeIn(500);
        $(this).parent('.dropdown').addClass('open');      
      }
      $(this).parent('.dropdown').find('.scroll_block').each(function(){
        $(this).tinyscrollbar_update();  
        if ($(this).find('.scrollbar.disable').length > 0) {
          $(this).addClass('full');
        } else {
          $(this).removeClass('full');
        }
      });  
    }    
  });

   $(document).click(function(e){
     var target = $(e.target);
     if (target.is('.dropdown, .dropdown_block, .ui-datepicker, .ui-datepicker-header a, .ui-datepicker-header a span') || target.parents('.dropdown, .dropdown_block').length) return;
        $('.dropdown_block').fadeOut(500);  
        $('.dropdown > span').removeClass('active');  
        $('.dropdown').removeClass('open');    
   });  

  $('body').on('click', '.dropdown_block .dropdown_close', function() {      
    $(this).parent('.dropdown_block').fadeOut(500,function() {
        $('.dropdown > span').removeClass('active');  
        $(this).parent('.dropdown').removeClass('open');          
      });
  });
}

//Help icon 
function helpIcon() {
  $('body').on('click', '.help > span', function(){    
    if ($(this).hasClass('active')) {
      $(this).next('.block-help').fadeOut(500,function() {
        $('.help > span').removeClass('active');  
      });   
    }
    else {
      if($(this).parents('.settings, .st-settings').length && !$(this).parents('.dropdown_block').length) {
        $('.dropdown > span').removeClass('active');
        $('.dropdown_block').fadeOut(500)
      }  
      $('.help > span').removeClass('active');
      $('.block-help').fadeOut(500)        
      $(this).addClass('active');
      $(this).next('.block-help').fadeIn(500);  
    }    
    $('.help').mouseleave(function(){
       var timeout = setTimeout(function(){
       $('.block-help').fadeOut(500,function() {
        $('.help > span').removeClass('active');  
      });
       }, 1000);
       $('.help').mouseenter(function(){
        clearTimeout(timeout);
       });
     });
  });
  
  $('body').on('click', '.block-help .dropdown_close', function(){  
    $(this).parent('.block-help').fadeOut(500);
    $('.help > span').delay(500).removeClass('active');
  });  
}  

//Tabs  
function tabs() {
  $('body').on('click', '.tabs a', function(e){
    e.stopPropagation();
    e.preventDefault();
    $(this).parent().find('a').removeClass('active');
    $(this).addClass('active');

    var TabId = $(this).attr('href');
    $(this).siblings('a').each(function(){
      var tId = $(this).attr('href');
      $(tId).removeClass('active');
    });
    
    $(TabId).addClass('active');  

    $(TabId).find('.scroll_block').each(function() {
      $(this).tinyscrollbar_update();   
      if ($(this).find('.scrollbar.disable').length > 0) {
        $(this).addClass('full');
      } else {
        $(this).removeClass('full');
      }
    });    
  });
}



$(function(){

  customSelect(); 
  tableStriped();  
  modalWindow(); 
  dropdown();
  helpIcon();
  tabs();



  //Sticky header
  if($('.logo').length){

    $(window).load(function(){

      var logoTop = $('.logo').offset().top;
      var logoLeft = $('.logo').offset().left;
      var logoHeight = $('.logo').outerHeight();
      var nextBlockpos = $('#st_header').next().outerHeight() + $('#st_header').outerHeight() - 1;

    if($(window).width() > 767) {
      $(window).scroll(function () {

          
        if(!$('#st_header .logo').hasClass('fixed') && $(window).scrollTop() > logoTop) {
          $('#st_header .logo').addClass('fixed').css('padding-left', logoLeft);  
          $('#st_header .logo').next().css('margin-top', logoHeight);
          $('#st_header .logo').removeClass('b_bottom');
        } else if ($('#st_header .logo').hasClass('fixed') && $(window).scrollTop() < logoTop) {
          $('#st_header .logo').removeClass('fixed').css('padding-left', 0);
          $('#st_header .logo').next().css('margin-top', 0);
          $('#st_header .logo').removeClass('b_bottom');
        } else if ($('#st_header .logo').hasClass('fixed') && $(window).scrollTop() > nextBlockpos - logoHeight){
          $('#st_header .logo').addClass('b_bottom');
        } else if ($('#st_header .logo').hasClass('fixed') && $(window).scrollTop() <  nextBlockpos - logoHeight) {
          $('#st_header .logo').removeClass('b_bottom');    
        }    
      });
    }

    });

  }    

   //Top menu functions

   $('.menu h1').each(function(){
    $(this).mouseover(function(){
      $(this).parent().addClass("active");
    });

      $(this).parent().mouseleave(function(){
      $(this).removeClass("active");
    });
    });

  $('.my-nav h1').click(function(){
    $(".my-nav").toggleClass("active");
  });

   $(document).click(function(e){
     var target = $(e.target);
     if (target.is('.my-nav') || target.parents('.my-nav').length) return;
    $(".my-nav, .my-nav > ul li").removeClass("active");
    $(".my-nav > ul li").find('ol').hide();
   });
   
    $('.my-nav').mouseleave(function(){
     var timeout = setTimeout(function(){
      $(".my-nav, .my-nav > ul li").removeClass("active");
     $(".my-nav > ul li").find('ol').hide();
     }, 1000);
     $('.my-nav').mouseenter(function(){
      clearTimeout(timeout);
     });
  });
     
  $('body').click(function(){
      $('.my-nav, .account, .sign-in, .services, .my-nav *, .account *, .sign-in *, .services *').removeClass("active").blur();
    });
    
    $('.my-nav, .account, .sign-in, .services').click(function(event) {
      event.stopPropagation();
  });

  $('.my-nav > ul li').click(function(){
    if ($(this).children('ol').length > 0){
    $(this).addClass('active').find('ol').slideDown(300);
    }
  });


//Social navigation 
                  
  $('.social_links').parent().mouseenter(function() {
     setTimeout(function(){
      $(".share_buttons").removeClass('hidden');
     }, 200);   
  });
  
  
    $('.social_links').parent().mouseleave(function(){
     var timeout = setTimeout(function(){
      $(".share_buttons").addClass('hidden');
     }, 1000);
     $(this).mouseenter(function(){
      clearTimeout(timeout);
     });
  });


// Custom scrollbar    
  $('.scroll_block').each(function(){
    $(this).tinyscrollbar();
    if ($(this).find('.scrollbar.disable').length > 0) {
      $(this).addClass('full');
    } else {
      $(this).removeClass('full');
    }
  });



// Persentile sliders 1-100
  $('.percentile.slider_max').each(function() {
    $(this).slider({
      range: "max",
      min: 1,
      max: 100,
      value: 90,
      slide: function( event, ui ) {
        $(this).find('a').text(ui.value);
      }
    });  
  });  
  $('.percentile.slider_max a').each(function() {
    $(this).text($(this).parent('.percentile.slider_max').slider( "value" ));
  });


  $('.percentile.slider_min').each(function() {
    $(this).slider({
      range: "min",
      min: 1,
      max: 100,
      value: 90,
      slide: function( event, ui ) {
        $(this).find('a').text(ui.value);
      }
    });  
  });  
  $('.percentile.slider_min a').each(function() {
    $(this).text($(this).parent('.percentile.slider_min').slider( "value" ));
  });

// Persentile sliders 1-20
  $('.percentile.slider_max20').each(function() {
    $(this).slider({
      range: "max",
      min: 1,
      max: 20,
      value: 90,
      slide: function( event, ui ) {
        $(this).find('a').text(ui.value);
      }
    });  
  });  
  $('.percentile.slider_max20 a').each(function() {
    $(this).text($(this).parent('.percentile.slider_max20').slider( "value" ));
  });


//Mobile functions
// Bottom links reports drop-down  
  if($(window).width() < 767) {
    $('.bottom-links h3').click(function(){
      $(this).next('ul').slideToggle(300);
    });
  }

// Available reports drop-down
  if($(window).width() < 767) {
    $('.items-av h1').click(function(){
      $(this).next('ul').slideToggle(300);
    });
  }

  
// Radio buttons  
  $('.btn-group[data-toggle="buttons-radio"]').children().click(function() {
    $(this).parent().find('.active').removeClass('active');
    $(this).addClass('active');
    var buttonId = $(this).attr('data-id');
    $(this).siblings().each(function(){
      var bId = $(this).attr('data-id');
      $(bId).removeClass('active');
    });
    $(buttonId).addClass('active');  
  });

// Check buttons  
  $('.btn-group[data-toggle="buttons-check"]').children().click(function() {
    $(this).toggleClass('active');
  });    
    
// Custom radiobuttons
      

    $('.modal-radio').click(function(){
    $('.modal-radio input').attr('checked', false);
    $(this).find('input').attr('checked',true);
    $('.modal-radio').each(function(){
      var attr = $(this).children('input').attr('checked');
      if(typeof attr !== 'undefined' && attr !== false){
        $('.modal-radio').removeClass('c_on');
        $('.modal-radio').parentsUntil('tbody').css('background-color','transparent');
        $(this).addClass('c_on');
        $(this).parentsUntil('tbody').css('background-color','#FFF7DB');
        if (typeof(custom_radio_change_callback) == 'function') {
          var input = $(this).children('input');
          custom_radio_change_callback(input.attr('name'), input.attr('id'));
        }
      }
    });
    });

  
    $('body').on('click', '.custom-radio', function(){
    $('.custom-radio input').attr('checked', false);
    $(this).find('input').attr('checked',true);
    $('.custom-radio').each(function(){
      var attr = $(this).children('input').attr('checked');
      
      if(typeof attr !== 'undefined' && attr !== false){
        $('.custom-radio').removeClass('c_on');
        $(this).addClass('c_on');
        if (typeof(custom_radio_change_callback) == 'function') {
          var input = $(this).children('input');
          custom_radio_change_callback(input.attr('name'), input.attr('id'));
        }
      }
    });
    });  
  
  

//Sortable Table 

  // add digicert site seal
  if ($('#DigiCertClickID_mFl0Bitm').length > 0) {
    __dcid = __dcid || [];__dcid.push(["DigiCertClickID_mFl0Bitm", "10", "s", "black", "mFl0Bitm"]);(function(){var cid=document.createElement("script");cid.async=true;cid.src="//seal.digicert.com/seals/cascade/seal.min.js";var s = document.getElementsByTagName("script");var ls = s[(s.length - 1)];ls.parentNode.insertBefore(cid, ls.nextSibling);}());
  }
  
  // close modal window when credit card button clicked
  $('.stripe-button button').click(function(){
    $('.modal-backdrop, .modal').hide().removeClass('active');
  });
  
});

$(document).ready(function() {
  if (jQuery().tablesorter) {
    $('table.sortable').tablesorter({
      textExtraction: function(node) {
        var attr = $(node).attr('data-metric');
        if (!attr) attr = $(node).text();
        if ($.isNumeric(attr)) attr *= -1;
        else if (typeof attr == 'string' || attr instanceof String) {
          val = attr.toLowerCase();
          attr = '';
          for(var i=0; i<=5; i++) {
            var code = '';
            if (i<val.length) code = (val.charCodeAt(i)+3).toString();
            while(code.length < 3) code += '0';
            attr = attr.concat(code);
          }
          attr *= -1;
        }
        return attr;
      }
    }).bind("sortEnd", function() {
      $(this).find('tbody td, tbody th').css('background-color', 'transparent');         
      tableStriped();
    });
  }
});

// close any active modal
function ch_close_modal() {
  $('.modal-backdrop, .modal, .secure, .pbs').hide().removeClass('active');
}


/**
 * columnizes the list(s) identified by selector. to do so it creates sibling 
 * lists and attempts to proportionately place the list items into those. Lists
 * with headers will be preserved such that items within a heading are not 
 * split into separate columns
 * @param mixed selector jquery selector for the lists (ol or ul)
 * @param int columns the number of columns to create
 * @return void
 */
function columnize_list(selector, columns) {
  // console.log("Columnizing into " + columns + " columns using selector with " + $(selector).length + " lists");
  $(selector).each(function() {
    var sections = [];
    var section = 0;
    var items = 0;
    if ($(this).is('ul') || $(this).is('ol') || $(this).is('div')) {
      // console.log("Columnizing list with " + $(this).find('> li').length + " elements");
      $(this).find('> ' + ($(this).is('div') ? 'dl' : 'li')).each(function(i, item) {
        if (sections.length && ($(item).has('h1').length || $(item).has('h2').length || $(item).has('h3').length || $(item).has('h4').length || $(item).has('h5').length)) section++;
        if (!(section in sections)) sections[section] = [];
        sections[section].push($(item).detach());
        items++;
      });
      var column = 0;
      var columnItems = 0;
      var rowsPerColumn = items/columns;
      var lists = [this];
      // console.log("Columnizing " + items + " items in " + sections.length + " sections into " + columns + " columns using " + rowsPerColumn + " rows per columns");
      while(lists.length < columns) {
        lists.push($(this).clone());
        $(this).parent().append(lists[lists.length - 1]);
        // console.log("Added sibling " + ($(this).is('ul') ? 'ul' : 'ol') + " element");
      }
      for(section in sections) {
        if (columnItems && (column + 1) < columns && (columnItems + sections[section].length) > rowsPerColumn) {
          column++;
          // console.log("Breaking to next column " + (column + 1) + " at " + columnItems + " column items");
          columnItems = 0;
        }
        for(var i=0; i<sections[section].length; i++) {
          $(sections[section][i]).appendTo(lists[column]);
          columnItems++;
          // console.log("Added row " + columnItems + " (" + $(sections[section][i]).html() + ") to column " + (column + 1) + ". List now has " + $(lists[column]).find('> li').length + " items");
          // no headers
          if (sections.length == 1 && columnItems >= rowsPerColumn) {
            column++;
            // console.log("Breaking to next column " + (column + 1) + " at " + columnItems + " column items");
            columnItems = 0;
          }
        }
      }
    }
  });
  // console.log("Done columnizing");
}

/**
 * returns a currency value using the appropriate currency prefix/suffic and 
 * rounding
 * @param float amount the amount
 * @param string currency the currency (default is USD)
 * @param int round an alternate rounding precision (default is 2)
 * @param boolean noformat don't format number with commas
 * @return string
 */
function formatCurrency(amount, currency, round, noformat) {
  var prefix = '$';
  var suffix = '';
  switch(currency) {
    case 'GBP':
      prefix = '&pound;';
      break;
    case 'EUR':
      prefix = '&euro;';
      break;
    case 'PLN':
      prefix = '';
      suffix = ' PLN';
      break;
    case 'CHF':
      prefix = '';
      suffix = ' CHF';
      break;
    case 'JPY':
      prefix = '&yen;';
      break;
  }
  // round if it isn't a whole number
  if ($.isNumeric(amount)) {
    round = $.isNumeric(round) && round>=0 ? round : 2;
    amount *= 1;
    if (Math.round(amount).toString() != amount.toString()) amount = amount.toFixed(round);
    if (noformat !== true) amount = formatNumber(amount);
    // remove trailing 3 zeros if present
    if (round > 3 && amount.toString().match(/\.[0-9]+000$/)) amount = amount.substr(0, amount.length - 3);
    // remove trailing 2 zeros if present
    if (round > 3 && amount.toString().match(/\.[0-9]+00$/)) amount = amount.substr(0, amount.length - 2);
    // change 3 decimal precision to 2 if the last 2 digits are zeros
    if (round == 3 && amount.toString().match(/\.[0-9]+00$/)) amount = amount.substr(0, amount.length - 1);
  }
  return prefix + amount + (suffix ? ' ' + suffix : '');
}

/**
 * formats a number by adding thousands place commas
 * @param float num the number to format
 * @return string
 */
function formatNumber(num) {
  if ($.isNumeric(num)) {
    var temp = num.toString().split('.');
    temp[0] = temp[0].replace(/\B(?=(\d{3})+(?!\d))/g, ",");
    num = (temp[0] + (temp.length > 1 ? '.' + temp[1] : ''));
  }
  return num;
}

/**
 * returns an string representing a size (GB, TB or PB) using the lowest 
 * possible whole number
 * @param float gb the size in gigabytes to convert
 * @param int round an alternate rounding precision (default is 2)
 * @return string
 */
function formatSize(gb, round) {
  var amount = gb;
  var label = 'GB';
  if ((amount/1024) > 1) {
    amount = amount/1024;
    label = 'TB';
    if ((amount/1024) > 1) {
      amount = amount/1024;
      label = 'PB';
    }
  }
  // round if it isn't a whole number
  if (Math.round(amount) + '' != amount + '') amount = amount.toFixed($.isNumeric(round) ? round : 2);
  return amount + label;
}