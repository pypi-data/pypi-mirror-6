(function ($) {
    $(document).ready(function () {
        $('#addForm').submit(function () {
            return false;
        });
        $('#add-btn').click(function () {
            $.ajax({
                type: "POST",
                url: '/ajax/add/',
                dataType: 'json',
                data: $('#addForm').serializeArray(),
                success: function () {
                    alert("Feed successfully added.");
                },
                error: function () {
                    alert("Error when trying to add feed. Try again later.");
                },
            });
        });
    })
})(jQuery);
