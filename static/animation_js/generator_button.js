$(document).ready(function() {
    $("#obliczenia").click(function() {
      // disable button
      $(this).prop("disabled", true);
      // add spinner to button
      $(this).html(
        `<span class="spinner-border spinner-border-sm" role="status" aria-hidden="true"></span> Loading...`
      );
    });
});
$(document).ready(function() {
    $('#obliczenia').click(function(){
        $.ajax({
            url: "/Generate_PID",
            type: "GET",
            success: function(response) {
                window.location.href = window.location.href;
                },
        });
    });
});
