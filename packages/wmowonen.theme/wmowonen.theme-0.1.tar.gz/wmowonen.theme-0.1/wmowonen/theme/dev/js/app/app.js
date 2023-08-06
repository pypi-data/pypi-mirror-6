$(function() {
  
  $('.navbar-form .form-control').addClass('hidden-lg hidden-md');
  
  $('.navbar-form button').click(function( event ) {
    if( $('.navbar-form .form-control').is(':hidden') ) {
      event.preventDefault();
    }
    
    $('.navbar-form .form-control').removeClass('hidden-lg hidden-md');
    
  });

});