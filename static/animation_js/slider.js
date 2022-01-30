$(document).ready(function () {

    //Okres próbkowania
    const $sample_time_value = $('.sample_time_value');
    const $sample_time_range = $('#sample_time_range');

    $sample_time_value.html($sample_time_range.val());
    $sample_time_range.on('input change', () => {
        $sample_time_value.html($sample_time_range.val());
    })

    //Czas wyprzedzenia
    const $differential_time_value = $('.differential_time_value');
    const $differential_time_range = $('#differential_time_range');

    $differential_time_value.html($differential_time_range.val());
    $differential_time_range.on('input change', () => {
        $differential_time_value.html($differential_time_range.val());
    })

    //Czas zdwojenia
    const $integration_time_value = $('.integration_time_value');
    const $integration_time_range = $('#integration_time_range');

    $integration_time_value.html($integration_time_range.val());
    $integration_time_range.on('input change', () => {
        $integration_time_value.html($integration_time_range.val());
    })

    //Wartość wzmocnienia regulatora
    const $gain_value = $('.gain_value');
    const $gain_range = $('#gain_range');

    $gain_value.html($gain_range.val());
    $gain_range.on('input change', () => {
        $gain_value.html($gain_range.val());
    })

    //Wartość zadana
    const $h_z_value = $('.h_z_value');
    const $h_z_range = $('#h_z_range');

    $h_z_value.html($h_z_range.val());
    $h_z_range.on('input change', () => {
        $h_z_value.html($h_z_range.val());
    })

})