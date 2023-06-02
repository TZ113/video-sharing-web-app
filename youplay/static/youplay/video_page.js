

const plus = document.getElementById('video_page_plus');
const video_id = document.getElementById('video_id').innerHTML;

if (plus) {
    plus.addEventListener('click', () => {
        showPlaylistModal(video_id);
    })
}

// Handle comments by the users
const commentForm = document.getElementById('comment_form');
if (commentForm) {
    commentForm.addEventListener('submit', (event) => {

        event.preventDefault();

        // Check whether any user is logged in, redirect to login page if none is
        checkLogin()

        const errorDiv = document.getElementById('error_message_div');

        // Send a POST request to the server using the fetch API with the users comment and id of the video that was commented on
        fetch('/home/comments', {
            method: "POST",
            headers: {
                'X-CSRFToken': event.target.children[0].value
            },
            body: JSON.stringify({
                'comment': document.querySelector('#comment_area').value,
                'video_id': video_id
            })
        })
            .then((response) => {
                console.log(response);
                if (response.status === 201) {
                    response.json().then(result => {
                        event.target.reset();
                        errorDiv.innerHTML = '';

                        // Dynamically create a div and add the comment to it
                        const wrapper = document.createElement('div');
                        wrapper.classList.add('comment_wrapper');
                        wrapper.innerHTML = `<div class="comment"><pre>${result['comment'].comment}</pre>
                    <div style="text-align: right;">&#8212 <a href="/users/user_profile">${result['comment'].commenter}</a></div></div>`;

                        // Add the div to the top of the documents 'comments' section
                        document.querySelector('#comments').prepend(wrapper);
                        document.getElementById('comments_div').classList.remove('d-none');
                    })
                }
                else {
                    response.json().then(result => {
                        if (result['error']) {
                            result['error'].forEach((elm) => {
                                console.log(elm);
                                errorDiv.innerHTML += `<small><strong>${elm}</strong></small><br>`;
                            })
                        }

                    })
                }
            })

            .catch(error => console.log(error))
    })
}

// Update likes
const like = document.querySelector('i.fa-heart');
if (like) {
    like.addEventListener('click', (evt) => {
        checkLogin()

        // Send a POST request to the server using fetch API with the video id to update 'like' 
        fetch(`/home/update_video/${video_id}`, {
            method: "PUT",
            headers: {
                'X-CSRFToken': evt.target.parentElement.children[4].value
            },
            body: JSON.stringify({
                updating: 'like'
            })
        })
            .then(response => response.json())
            .then(result => {

                // Update the icon based on whether it's a like or unlike
                if (result.status === 'like') {
                    evt.target.classList.replace('fa-regular', 'fa-solid');
                }
                else {
                    evt.target.classList.replace('fa-solid', 'fa-regular');
                }

                // Update the like count
                evt.target.nextElementSibling.innerHTML = result.likes;
            })
            .catch(error => console.log(error))
    })
}


const video = document.querySelector('video');

// Create an IntersectionObserver to check if a video has been watched 
const videoObserver = new IntersectionObserver((entries) => {

    entries.forEach((entry) => {

        // If more than 70% of the video is in the viewport
        if (entry.isIntersecting && entry.intersectionRatio >= 0.7) {
            video.addEventListener('play', () => {
                const interval = setInterval(() => {

                    // Checks if the user has watched at least 70% of the video
                    if (video.currentTime / video.duration >= .75) {
                        clearInterval(interval);
                        console.log("user has watched at least 70% of the video");

                        // Send a PUT request using the fetch API to update the video view count
                        fetch(`/home/update_video/${video_id}`, {
                            method: "PUT",
                            headers: {
                                'X-CSRFToken': video.nextElementSibling.value
                            },
                            body: JSON.stringify({
                                updating: 'view'
                            })
                        })
                            .then(response => response.json())
                            .then(result => {
                                document.querySelector('#views').innerHTML = result['views'];
                            })

                            .catch(error => console.log(error))
                    }
                }, 1000)
            })
        }
    });
}, { threshold: 0.5 });

videoObserver.observe(video);

// Get the clickable elements for editing the videos description (only for the uploader)
const editVideoDescription = document.querySelector('.edit_video_description');
if (editVideoDescription) {

    // Displays the edit description form upon clicking 
    editVideoDescription.addEventListener('click', (event) => {
        event.target.parentElement.classList.add('d-none');
        document.getElementById('div_description_form').classList.remove('d-none');
    })
}

// If the form comes back invalid
const errorDiv = document.getElementById('description_form_error');
if (errorDiv && errorDiv.innerHTML === 'True') {
    console.log("error");
    if (editVideoDescription) editVideoDescription.parentElement.classList.add('d-none');
    document.getElementById('div_description_form').classList.remove('d-none');
}


const deleteVideoYes = document.getElementById("delete_video_yes");

// handle users deletion of videos
if (deleteVideoYes) {
    deleteVideoYes.addEventListener('click', (evt) => {
        
        fetch(`/home/delete_video/${video_id}`, {
            method: "DELETE",
            headers: {
                'X-CSRFToken': evt.target.nextElementSibling.value
            }
        })
            .then(response => {
                console.log(response);
                if (response.status === 204) {
                    location.href = `/home?message=Video successfully deleted.`;
                } else {
                    console.log(response.status);
                }
            })
            .catch(error => console.log(error))
    })
}

