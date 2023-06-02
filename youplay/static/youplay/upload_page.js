
// Toggle the upload modal on page load
document.addEventListener('DOMContentLoaded', () => {
    $('#uploadModal').modal('toggle');
})

// Get references to necessary HTML elements
document.getElementById('div_id_uploader');
const uploader = document.getElementById('id_uploader');
const user_id = document.getElementById('user_id').innerHTML;

const title = document.getElementById('uploadModalLabel');
const uploadForm = document.getElementById('upload_form');
const progressWrapper = document.querySelector('.progress_wrapper');
const progressBar = document.getElementById('progress_bar');
const uploadButton = document.getElementById('upload_button');
const uploadDone = document.getElementById('progress_end');

const preventClick = (e) => {
    e.preventDefault();
}

// handles the form submission
uploadForm.onsubmit = (e) => {
    e.preventDefault();

    // Set the uploader value to the current users id
    uploader.value = user_id;

    // Create a new formData object from the upload form
    formData = new FormData(e.target);

    // Create a new XHR object to send the upload request to the server 
    let xhr = new XMLHttpRequest();
    xhr.open("POST", "/home/upload", true);

    // Show the progress bar and prevent click event for the upload button once the upload starts
    xhr.upload.onloadstart = (e) => {
        uploadDone.classList.add('d-none');
        progressBar.classList.remove('d-none');
        progressWrapper.classList.remove('d-none');
        uploadButton.addEventListener('click', preventClick);
        document.getElementById('top').scrollIntoView();
    }

    // Update the progress bar as the upload progresses
    xhr.upload.onprogress = (e) => {
        if (e.lengthComputable) {
            const percentProgress = (e.loaded / e.total) * 100;
            progressBar.innerHTML = `<div class="progress-bar progress-bar-striped progress-bar-animated" 
                    role="progressbar" style="width: ${percentProgress}%" aria-valuenow="${percentProgress}" aria-valuemin="0" 
                    aria-valuemax="100">${Math.round(percentProgress)}%</div>`
        }
    }

    // Handle the end of upload 
    xhr.onloadend = (e) => {
        uploadForm.reset();

        const response = JSON.parse(xhr.response);
        console.log(xhr, xhr.response);
        // If the upload is successful, shows the appropriate message
        if (xhr.status === 201) {
            progressWrapper.classList.add('d-none');
            uploadDone.classList.remove('d-none');
            // fetch(`/home/processing_status?id=${response['video_id']}`)
            //     .then(response => response.json())
            //     .then(result => {
            //         if (result.processing) {
            //             console.log("uploaded and processing")
            //             uploadDone.innerHTML = 'The video is successfully uploaded and now being processed. This may take a while and no upload can be performed while this is happening. Please, be patient!';
            //         }
            //     })
        }

        // If the upload was unsuccessful, shows the appropriate error messages
        else if (xhr.status === 400) {

            // Remove the previous error messages, if any
            const pre_error_div = document.querySelectorAll('.upload_error_message');
            if (pre_error_div) {
                pre_error_div.forEach(elm => {
                    elm.remove();
                })
            }
            progressWrapper.classList.add('d-none');

            const responseArray = Object.entries(response['error_messages']);

            // Display the error messages
            for (let i = 0; i < responseArray.length; i++) {
                const messageDiv = document.createElement('div');
                messageDiv.classList.add('upload_error_message');
                if (responseArray[i][1].length > 1) {
                    for (j in responseArray[i][1]) {
                        console.log(j);
                        messageDiv.innerHTML += `${responseArray[i][1][j]} <br>`;
                    }
                } else {
                    messageDiv.innerHTML = responseArray[i][1];
                }
                if (responseArray[i][0] === 'all') {
                    const btn = document.getElementById('upload_button_div');
                    btn.insertAdjacentElement('beforebegin', messageDiv)
                } else {
                    const hint = document.getElementById(`hint_id_${responseArray[i][0]}`);
                    hint.insertAdjacentElement('beforebegin', messageDiv);
                }
                messageDiv.scrollIntoView();
            }

        }

        uploadButton.removeEventListener('click', preventClick)

    }

    // Send the data to the server
    xhr.send(formData)


}

// Bring the focus on the title input of the form once the upload modal is shown 
$('#uploadModal').on('shown.bs.modal', (e) => {
    $('#id_title').trigger('focus');
})


// When the upload modal is closed redirect to the home page
$('#uploadModal').on('hide.bs.modal', (e) => {
    location.href = '/home';
})