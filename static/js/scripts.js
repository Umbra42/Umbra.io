document.getElementById('uploadBtn').addEventListener('click', function() {
    console.log(" > upload button clicked");
    const uploadFrom = document.getElementById('uploadForm');
    console.log("upload form identified");
    const formData = new FormData(uploadFrom)
    console.log("form data constructed");
    console.log("fetching upload meta data from /upload");
    $.ajax({
        url: '/upload',
        method: 'POST',
        data: formData,
        processData: false,
        contentType: false,
        success: function(data) {
            let taskId = data.task_id;
            sessionStorage.setItem('task_id', taskId);
            console.log(" > calling pollProgress");
            pollProgress(taskId);
        },
        error: function() {
            console.error("upload failed");
        }
    });
});

function pollProgress(taskId) {
    console.log(" > pollProgress called");
    function updateProgress() {
        console.log(" > updateProgress called");
        console.log(window.location.pathname);
        if (window.location.pathname !== '/BASE') {
            console.log("window not /BASE");
            return;
        }
        console.log("starting ajax for progress modal");
        $.ajax({
            url: "/upload-progress/${taskId}",
            success: function(data) {
                console.log("fetched progress data:");
                console.log(data);
                $("#currentTask").text(data.status);
                console.log("determining progress %");
                let overallProgress = (data.current / data.total) * 100;
                console.log("progress: ", overallProgress, " = ", data.current, " / ", data.total, " * ", 100);

                console.log("hooking progress to modal");
                $("#overallProgress").css(
                    "width", overallProgress + "%").attr(
                        "aria-valuenow", overallProgress).text(
                            overallProgress + "%");
            
                console.log("clearing progress bar");
                $("#fileProgressContainer").empty(); // Clear current file progress bars
                console.log(data.fileProgress);
                if (data.fileProgress) {
                    console.log("feeding progress data to bar");

                    data.fileProgress.forEach(function(file) {
                        var fileProgressBar = $('<div class="progress-bar" role="progressbar"></div>')
                                                .css("width", file.progress + "%")
                                                .attr("aria-valuenow", file.progress)
                                                .text(file.fileName + ": " + file.progress + "%");
                        $("#fileProgressContainer").append(fileProgressBar);
                    });
                }
                
                console.log("determining blender");
                console.log(data.blenderInstallation);
                console.log(data.blenderInstallation.required);
                if (data.blenderInstallation && data.blenderInstallation.required) {
                    console.log("show blender installation progress bar");
                    $("#blenderProgress").css(
                        "width", data.blenderInstallation.progress + "%").attr(
                            "aria-valuenow", data.blenderInstallation.progress).text(
                                "Blender Installation: " + data.blenderInstallation.progress + "%");
                } else {
                    console.log("hide blender installation progress bar");
                    $("#blenderInstallationSection").hide();
                }

                console.log("update task lenght");
                if (data.current < data.total) {
                    setTimeout(updateProgress, 1000);
                } else {
                    sessionStorage.removeItem('task_id');
                }
            },
            error: function() {
                console.error("could not fetch progress data");
            }
        });
    }
    console.log(" > calling updateProgress");
    updateProgress();
}
                

$(document).ready(function() {
    if (window.location.pathname === '/BASE') {
        let taskId = sessionStorage.getItem('task_id');
        console.log("task: ", taskId);
        if (taskId) {
            pollProgress(taskId);
        }
    }
});
