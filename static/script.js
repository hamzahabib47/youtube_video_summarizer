$('#input-form').on('submit', function (e) {
    e.preventDefault();

    const submitButton = $('#submit-btn');
    const buttonText = $('#button-text');
    const loader = $('#loader');

    // Disable the button and show loader
    submitButton.prop('disabled', true);
    buttonText.addClass('d-none'); // Hide button text
    loader.removeClass('d-none'); // Show loader

    // Perform the AJAX request
    $.post('/process', $(this).serialize(), function (data) {
        // Re-enable the button and restore text
        submitButton.prop('disabled', false);
        buttonText.removeClass('d-none'); // Show button text
        loader.addClass('d-none'); // Hide loader

        // Handle the response
        if (data.includes('Error')) {
            $('#output').removeClass('d-none').text(data).css('color', '#ff4444');
        } else {
            $('#output').removeClass('d-none').html(data).css('color', '#ffffff');
        }
    });
});