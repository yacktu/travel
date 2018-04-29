$(function () {
    $('#submit').click(function () {
        console.log("Clicked.");

        $.ajax({
            url: '/bookTrip',
            data: $('form').serialize(),
            type: 'POST',
            success: function (response) {
                console.log(response);
            },
            error: function (error) {
                console.log(error);
            }
        });
    });
});