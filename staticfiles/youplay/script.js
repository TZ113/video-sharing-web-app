
let counter = 0;
const quantity = 20;
document.addEventListener('DOMContentLoaded', load);

window.onscroll = () => {
    if (window.innerHeight + window.scrollY >= document.body.offsetHeight) {
        load()
    }
}


function load() {
    const start = counter;
    const end = start + quantity - 1;
    counter = end + 1;
    if (location.pathname.startsWith('/home/video/')){
        console.log(location.pathname)
        console.log('/video/')
        fetch(`/home/comments?video_id=${document.querySelector('#video_id').innerHTML}&start=${start}&end=${end}`)
    .then(response => response.json())
    .then(result => {
        console.log(result)
        result_sorted = result.sort(function(a,b) {
            return new Date(b.timestamp) - new Date(a.timestamp)
        })
        result_sorted.forEach(add_comment);
    })
    }  
    else if (location.pathname.startsWith('/home/profiles/')){
        console.log(location.pathname)
        console.log('/profile/')
        fetch(`/home/profiles/${document.querySelector('#user_id').innerHTML}?start=${start}&end=${end}`)
        .then(response => response.json())
        .then(result => {
            result_sorted = result.sort(function(a, b) {
                return new Date(b.timestamp) - new Date(a.timestamp)
            })

            result_sorted.forEach(add_video);
            if (document.querySelector('#videos').innerHTML === ''){
                document.querySelector('#videos').innerHTML = `<h3>${document.querySelector('#profile_name').innerHTML} has not uploaded any videos yet!</h3>`
            }
        })
    }
    else if (location.pathname.startsWith('/home/')){
        console.log(location.pathname)
        console.log('/home/')
        fetch(`/home/?start=${start}&end=${end}`)
        .then(response => response.json())
        .then(result => {
            result_sorted = result.sort(function(a, b) {
                return new Date(b.timestamp) - new Date(a.timestamp)
            })
            result_sorted.forEach(add_video);
        })
    }
}


function add_video(content) {
    const anchor = document.createElement('a');
    anchor.id = "video";
    anchor.href = `/home/video/${content.id}`;
    const uploader = content.uploader.charAt(0).toUpperCase() + content.uploader.slice(1); 
    const a = `<div id="stuff_processing">
        <img src="/home/uploads/${content.thumbnail}" alt="thumbnail for ${content.title}"  width="300" height="200">
    <div id="title_flex">${content.title}</div>
    <div id="uploader">${uploader}</div>
    <div style="color:gray;">This video is still being processed</div></div>`
    const b = `<div id="stuff_processed">
        <img id="thumb" src="/home/uploads/${content.thumbnail}" alt="thumbnail for ${content.title}" width="300" height="200">
    <div id="title_flex">${content.title}</div>
    <div id="uploader">${uploader}</div>
    <div>${content.views} views | ${content.time_passed_since_added} ago</div>
</div>`
    if (content.processing === true){
        anchor.innerHTML = a;
        fetch(`/home/processing_status?id=${content.id}`)
        .then(response => response.json())
        .then(result => {
            if (result.processing === false){
                anchor.innerHTML = b;
            }
        })
        .catch(error => console.log(error))
    }
    else{
        anchor.innerHTML = b;
    }
    document.querySelector('#videos').append(anchor); 
}


function add_comment(content) {
    console.log(document.getElementById('user').innerHTML, content.commenter_id)
    const wrapper = document.createElement('div');
    wrapper.classList.add('comment_wrapper');
    const commenter = content.commenter.charAt(0).toUpperCase() + content.commenter.slice(1); 
    if (document.getElementById('user').innerHTML == content.commenter_id){
        console.log('uploader is user')
        wrapper.innerHTML = `<div class='comment'><pre>${content.comment}</pre>
        <div style="text-align: right;">&#8212 <a href="/users/user_profile">${commenter}</a></div></div>`;    
    }
    else{
        wrapper.innerHTML = `<div class='comment'><pre>${content.comment}</pre>
        <div style="text-align: right;">&#8212 <a href="/home/profiles/${content.commenter_id}">${commenter}</a></div></div>`;
    }
    
    document.querySelector('#comments').append(wrapper);
}


function subscribe_unsubscribe(event, user_id) {
    if (document.querySelector('#user').innerHTML === 'None') {
        location.href = '/users/login'
    }
    else {
        fetch('/home/subscribe_unsubscribe', {
            method: 'PUT',
            headers: {
                'X-CSRFToken': event.target.previousElementSibling.value
            },
            body: JSON.stringify({
                'user_id': user_id
            })
        })
        .then (response => response.json())
        .then(result => {
            if (event.target.innerHTML === 'Subscribe'){
                event.target.innerHTML = 'Unsubscribe';
            }
            else {
                event.target.innerHTML = 'Subscribe';
            }
            event.target.parentElement.children[1].innerHTML = result['subscribers'];
            })
        .catch(error => console.log(error))
    }
    
}
