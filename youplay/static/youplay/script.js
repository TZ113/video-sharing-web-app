// Set counter and quantity for the load function
let counter = 0;
const quantity = 20;

const videos = document.querySelector('.videos');

// Dynamically create HTML content for each of the videos and then add them to 'videos'
const addVideo = (content) => {

    // Create a hyperlink element and set its properties
    const anchor = document.createElement('a');
    anchor.classList.add("video");
    anchor.href = `/home/video/${content.slug}`;

    const uploader = content.uploader.charAt(0).toUpperCase() + content.uploader.slice(1); // Uploader of the video
    const thumbnailPath = "/media/" + content.thumbnail;
    // Dynamically create content for videos 
    // Videos that are currently being processed
    const processing = `<div class="stuff_processing">
        <img src="/media/processing(high_res).jpg" alt="thumbnail for ${content.title}"  width="300" height="200">
    <div class="title_flex">${content.title}</div>
    <div class="uploader">${uploader}</div></div>`

    // Videos that aren't being processed
    const processed = `<div class="stuff_processed" style="position:relative;" onmouseleave="this.children[1].classList.add('d-none');">
        <img class="thumb" src="${thumbnailPath}" alt="thumbnail for ${content.title}" width="300" height="200">
        <div class="d-none" style="position:absolute; top: 5px; right:5px;">
                <i class="videos_plus fa-solid fa-plus"></i><span hidden>${content.id}</span>
        </div>     
        <div class="title_flex" data-toggle="tooltip" data-placement="top" title="${content.title}">${content.title}</div>
        <div class="uploader">${uploader}</div>
        <div class="views">${content.views} views | ${content.time_passed_since_added} ago</div>
    </div>`


    if (content.processing === true) {
        anchor.innerHTML = processing;

        // Ask the server whether the processing is finished
        fetch(`/home/processing_status?id=${content.id}`)
            .then(response => response.json())
            .then(result => {

                // If processing is finished change the content
                if (result['processing'] === false) {
                    const thumbnailPath = "/media/" + result['thumbnail_path']
                    console.log(thumbnailPath);
                    const processedModified = processed.replace(/src="\S+"\s/i, `src="${thumbnailPath}" `);
                    anchor.innerHTML = processedModified;
                }
            })
            .catch(error => console.log(error))
    }
    else {
        anchor.innerHTML = processed;
    }

    videos.append(anchor);
}

// Dynamically create HTML content for comments
const addComment = (content) => {

    const wrapper = document.createElement('div');
    wrapper.classList.add('comment_wrapper');
    const commenter = content.commenter.charAt(0).toUpperCase() + content.commenter.slice(1);

    // If the commenter is the current user hyperlink leads to the editable profile page
    if (document.getElementById('user_id').innerHTML == content.commenter_id) {
        wrapper.innerHTML = `<div class='comment'><pre>${content.comment}</pre>
        <div style="text-align: right;">&#8212 <a href="/users/user_profile">${commenter}</a></div></div>`;
    }

    // Else it leads to different non-editable profile page
    else {
        wrapper.innerHTML = `<div class='comment'><pre>${content.comment}</pre>
        <div style="text-align: right;">&#8212 <a href="/home/profiles/${content.commenter_id}">${commenter}</a></div></div>`;
    }

    document.querySelector('#comments').append(wrapper);
}

// Create a new IntersectionObserver object
const observer = new IntersectionObserver((entries) => {

    entries.forEach((entry) => {
        // If intersection happens call the 'load' function
        if (entry.isIntersecting) load()
    })
})

// Show a clickable 'fa-plus' icon on video items
const showAddVideoButton = (event) => {
    if (event.target.classList.contains('stuff_processed')) {

        event.target.children[1].classList.remove('d-none');
    }
    else if (event.target.classList.contains('fa-plus')) {
        return
    }
    else if (event.target.classList.contains('thumb') || event.target.classList.contains('uploader') || event.target.classList.contains('views')) {
        event.target.parentElement.children[1].classList.remove('d-none');
    }
}

// Modify and add playlist names to the specific element
const insertPlaylistName = (playlistName, elm) => {
    console.log("inserting playlist names");
    let playlistNameShort = '';
    if (playlistName.length > 30) {
        playlistNameShort = playlistName.slice(0, 29) + "&hellip;";
    } else {
        playlistNameShort = playlistName;
    }
    elm.innerHTML = `Playlist: ${playlistNameShort}`;
    elm.setAttribute("title", playlistName);
    const deletePlaylistButton = document.getElementById('delete_playlist_button');
    deletePlaylistButton.classList.remove('d-none');
}


// Fetch data from the server and load them to pages
const load = () => {
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;

    if (location.pathname.startsWith('/home/video/')) {

        // Send a GET request to the specified server endpoint using the fetch API with 'video_id' and 'start', 'end' values
        fetch(`/home/comments?video_id=${document.querySelector('#video_id').innerHTML}&start=${start}&end=${end}`)
            .then(response => {
                if (response.status === 200) {
                    response.json().then(result => {
                        result_sorted = result.sort(function (a, b) {
                            return new Date(b.timestamp) - new Date(a.timestamp)
                        })

                        result_sorted.forEach(addComment);
                        document.getElementById('comments_div').classList.remove('d-none');
                        // Set the observer for the last-child element of 'comments' div
                        const container = document.getElementById('comments');
                        const lastChild = container.querySelector('.comment_wrapper:last-child')
                        observer.observe(lastChild);
                    })
                }
            })

    }
    else if (location.pathname.startsWith('/home/')) {
        const title = document.getElementById("title");

        fetch(`${location.pathname}?&start=${start}&end=${end}`)
            .then(response => {
                if (response.status === 200) {
                    // Response has video data
                    response.json().then(result => {
                        // Get the first (only) key of the result object, which is the name of the list
                        const keyName = Object.keys(result)[0];

                        // If it's a playlist created by user
                        if (location.pathname.match(/^\/home\/list_videos\/[a-z0-9]+(?:-[a-z0-9]+)*$/i) && title.innerHTML === '') insertPlaylistName(keyName, title);

                        result[keyName].forEach(addVideo);

                        // Set the observer for the scrolling mechanism
                        const container = document.querySelector('.videos');
                        const lastChild = container.querySelector('.video:last-child')
                        observer.observe(lastChild);
                    })
                }
                else if (response.status === 206 && end < 20) {
                    // It's an empty list, only the name is returned
                    response.json().then(result => {
                        const keyName = result["list_name"];
                        if (location.pathname.match(/^\/home\/list_videos\[a-z0-9]+(?:-[a-z0-9]+)*$/i)) insertPlaylistName(keyName, title);
                    })
                }
            })
        // Set the value of the 'title' element for these paths
        if (location.pathname === '/home/list_videos/watchlater') {
            title.innerHTML = "Videos you selected for watching later..";
        }
        else if (location.pathname === '/home/list_videos/liked_videos') {
            title.innerHTML = "Your liked videos..";
        }
        else if (location.pathname === '/home/list_videos/uploaded_videos') {
            title.innerHTML = "Your uploaded videos..";
        }
    }
}

if (videos) {
    videos.addEventListener('mouseover', showAddVideoButton)

    videos.addEventListener('click', (e) => {
        if (e.target.classList.contains('videos_plus')) {
            e.preventDefault();
            const video_id = e.target.nextElementSibling.innerHTML;
            showPlaylistModal(video_id);
        }
    })
}

// Check whether any user is logged in, redirects to the login page if none
const checkLogin = () => {
    if (document.getElementById('user_id').innerHTML === 'None') {
        location.href = '/users/login'
    }
}

const checkboxContainer = document.getElementById('playlists_checkboxes_container');

// Add or remove videos from playlists and also create new ones
function updatePlaylists(event) {

    // If the user is trying to create a new playlist
    if (event.target.id === 'create_list_form') {
        event.preventDefault();
        const message = document.getElementById('create_list_input_message');
        message.classList.add('d-none');
        new_playlist_name = document.getElementById('create_list_input').value;

        // Prevent adding '<' or '>' into playlist names 
        if (new_playlist_name.includes('<') || new_playlist_name.includes('>')) {
            message.classList.remove('d-none');
        }

        // Create a new playlist
        else {

            // Send a POST request to the server endpoint with the new playlist's name
            fetch(`/home/update_playlists`, {
                method: "POST",
                headers: {
                    'X-CSRFToken': event.target.children[0].value
                },
                body: JSON.stringify({
                    'new_playlist_name': new_playlist_name,
                    'video_id': document.getElementById('vid_id').innerHTML
                })
            })
                .then(response => {
                    const message_div = document.getElementById('form_message');
                    message_div.classList.remove('alert-success', 'alert-danger')

                    // If new playlist is successfully created
                    if (response.status === 201) {
                        response.json().then(result => {
                            event.target.reset();
                            /* Dynamically create a new div and an input element of type checkbox with the playlists name as value and 'checked' attribute inside that div */
                            const div = document.createElement('div');
                            div.id = `${result['name']}_div`
                            div.innerHTML = `
                        <input type="checkbox" value="${result['name']}" id="${result['name']}_input" class="playlist form-check-input" checked>
                        <label for="${result['name']}_input" class="form-check-label">${result['name']}</label>
                        `
                            // Add the div to the container and display the success message
                            checkboxContainer.append(div);
                            message_div.classList.add('alert-success');
                            message_div.innerHTML = result['res'];
                            message_div.classList.remove('d-none');

                            // Add the playlist in the sidebar Playlists menu
                            const anchor = document.createElement('a');
                            anchor.href = `/home/list_videos/${result['slug']}`;
                            let name = result['name'];
                            if (name.length > 20) {
                                name = name.slice(0, 19) + "&hellip;";
                            }
                            anchor.innerHTML = `${name}`;
                            anchor.classList.add("w3-bar-item", "w3-btn", "w3-hover-indigo");
                            document.getElementById("playlists").prepend(anchor);
                        })
                    }

                    // If something went wrong
                    else if (response.status === 400 || response.status === 500) {
                        response.json().then(result => {

                            // Display the error message 
                            message_div.classList.add('alert-danger');
                            message_div.innerHTML = result['res'];
                            message_div.classList.remove('d-none');
                        })
                    }
                })
                .catch(error => console.log(error))
        }
    }

    // If the user is trying to update an existing playlist
    else {

        // Send a PUT request to the server endpoint with the name of the playlist
        fetch(`/home/update_playlists`, {
            method: "PUT",
            headers: {
                'X-CSRFToken': document.getElementById('create_list_form').children[0].value
            },
            body: JSON.stringify({
                'playlist_name': event.target.value,
                'video_id': document.getElementById('vid_id').innerHTML
            })
        })
            .then(response => response.json())
            .then(result => {

                // Display the response message
                const message_div = document.getElementById('list_message');
                message_div.innerHTML = result['res'];
                message_div.classList.remove('d-none')
            })
            .catch(error => console.log(error))
    }

}

/* Display the modal where user can add, remove the selected video to and from playlists they created,
and also create new playlist and add. */
const showPlaylistModal = (video_id) => {

    // Check if user is logged in
    checkLogin()

    // Prepare the modal for display
    checkboxContainer.innerHTML = '';
    document.getElementById('list_message').classList.add('d-none');
    document.getElementById('form_message').classList.add('d-none');
    document.getElementById('vid_id') ? document.getElementById('vid_id').remove() : '';

    // Send a GET request to the server for the names of all existing playlists created by the user
    fetch('/home/get_playlists')
        .then(response => response.json())
        .then(result => {

            for (let i in result) {

                // Dynamically create a div and set attributes
                const div = document.createElement('div');
                div.id = `${i}_div`
                div.classList.add('mb-2');

                // If the selected video already exists in a playlist
                if (result[i].includes(parseInt(video_id))) {

                    // Create an input element of type 'checkbox' with the playlists name and 'checked' attribute inside that div
                    div.innerHTML = `
                            <input type="checkbox" value="${i}" id="${i}_input" class="form-check-input playlist" checked>
                            <label for="${i}_input" class="form-check-label">${i}</label>
                            `
                }
                else {
                    // Create one without 'checked' attribute
                    div.innerHTML = `
                            <input type="checkbox" value="${i}" id="${i}_input" class="form-check-input playlist">
                            <label for="${i}_input" class="form-check-label">${i}</label>
                            `
                }

                checkboxContainer.append(div);
            }

            document.getElementById('Watch Later_div').style.order = -1;

            // Dynamically create a div and hide the 'video_id' in it for later use
            const vid_div = document.createElement('div');
            vid_div.innerHTML = video_id
            vid_div.classList.add('d-none');
            vid_div.id = 'vid_id';
            document.querySelector('#playlistModal .modal-body').append(vid_div);

            $('#playlistModal').modal('toggle');

        })
        .catch(error => console.log(error))
}

checkboxContainer.addEventListener('click', (e) => {
    if (e.target.classList.contains('playlist')) updatePlaylists(e);
})

// Handle subscriptions
const subscribeUnsubscribe = (evt) => {
    checkLogin();
    fetch('/home/subscribe_unsubscribe', {
        method: 'PUT',
        headers: {
            'X-CSRFToken': evt.target.previousElementSibling.value
        },
        body: JSON.stringify({
            'user_id': evt.target.nextElementSibling.innerHTML
        })
    })
        .then(response => response.json())
        .then(result => {
            console.log(result['status'], typeof result['status']);

            // Update the page based on the response
            if (result['status'] === 'subscribed') {
                evt.target.innerHTML = 'Unsubscribe';
            }
            else {
                evt.target.innerHTML = 'Subscribe';
            }
            evt.target.parentElement.children[1].innerHTML = result['subscribers'];
        })
        .catch(error => console.log(error))

}

const searchModalDialog = document.querySelector('#searchModal .modal-dialog');
const searchModalBody = document.querySelector('#searchModal .modal-body');
const searchModalTitle = document.querySelector('#searchModal .modal-title');

// Add results of the search query to the searchModal
const addResult = (content) => {

    // Dynamically create a div, and set attributes
    const div = document.createElement('div');
    div.classList.add('search_result');

    // Set the innerHTML of the div with necessary values
    const uploader = `<span class="uploader">${content[2].charAt(0).toUpperCase() + content[2].slice(1)}</span>`;
    div.innerHTML = `<a href="/home/video/${content[0]}">${content[1]} &nbsp;&nbsp;&nbsp;&nbsp;  &#8212;&nbsp;${uploader}</a>`;

    // Append the div to the modal
    searchModalBody.append(div);
}

// Handle search request for videos by the user
document.getElementById('search_form').addEventListener('submit', (event) => {
    event.preventDefault();
    const query = document.getElementById('query');

    // Not accepting an empty value
    if (query.value === '') return;
    else {
        // Send a get request to the server with the query 
        fetch(`/home/search?q=${query.value}`)
            .then(response => {

                // Prepare the searchModal for displaying results
                searchModalTitle.innerHTML = 'Search Results...'
                searchModalBody.innerHTML = '';
                searchModalDialog.classList.contains('modal-sm') ? searchModalDialog.classList.replace('modal-sm', 'modal-lg') : '';
                event.target.reset();
                // If the server returned a response with data
                if (response.status === 200) {
                    response.json().then(result => {
                        // Call the 'addResult' function for each item of the array
                        console.log(typeof response["matches"]);
                        result["matches"].forEach(addResult);
                    })
                }
                // If no data was returned
                else if (response.status === 204) {
                    searchModalBody.innerHTML = `No Matches.. SORRY!`
                    searchModalBody.style.color = 'gray';
                }
                // Display the response message on the modal in other cases
                else {
                    console.log(response);
                    searchModalBody.innerHTML = `${response.status} (${response.statusText}).`;
                    searchModalBody.style.color = 'red';
                }
                $('#searchModal').modal('toggle');
            })
            // I still don't understand which errors are caught by this, hope to learn!
            .catch(error => console.log(error))

    }
})

document.addEventListener('DOMContentLoaded', () => {
    if (location.pathname.startsWith('/home') && location.pathname != '/home/upload') load()
})


document.querySelectorAll('.subscription').forEach((elm) => {
    elm.addEventListener('click', subscribeUnsubscribe)
})
