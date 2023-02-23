$(document).ready(function () {
  let amenityList = [];
  $('input[type=checkbox]').change(function () {
    let name = $(this).attr('data-name');
    if ($(this).is(':checked')) {
      amenityList.push(name);
    } else {
      amenityList = amenityList.filter(amen => amen !== name);
    }
    $('.amenities h4').text(amenityList.join(', '));
  });

  // display red circle on top right of page if status is OK
  $.ajax({
    type: 'GET',
    url: 'http://0.0.0.0:5001/api/v1/status/',
    dataType: 'json',
    success: function (data) {
      if (data.status === 'OK') {
        $('#api_status').addClass('available');
      } else {
        $('#api_status').removeClass('available');
      }
    }
  });

});
