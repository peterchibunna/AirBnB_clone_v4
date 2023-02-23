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
});
