

// Get all the elements with edit button in an HTMLCollection
const pens = document.getElementsByClassName('fa-pen');

const modalTitle = document.getElementById('profileModalLabel');
const modalBody = document.querySelector('#mb');
const elements = modalBody.children; // Get all the hidden edit elements in modal body in an HTMLCollection

// Make the right form element visible while hiding the others
const showRightElement = (id) => {
    for (let i = 0; i < elements.length; i++) {
        if (elements[i].id === id) {
            if (elements[i].classList.contains('d-none')) {
                elements[i].classList.remove('d-none');
            }
        } else elements[i].classList.add('d-none');
    }
    // Toggle the modal after making the right form element visible on it
    $('#profileModal').modal('show');
}

const showUsernameChangeForm = () => {
    modalTitle.innerHTML = 'Update Username Here.. ';
    showRightElement('username_change_form_div');
}

const showEmailChangeForm = () => {
    modalTitle.innerHTML = 'Update Email Here..';
    showRightElement('email_change_form_div');
}

const showAboutForm = () => {
    modalTitle.innerHTML = 'Update About Info Here..';
    showRightElement('about_change_form_div');
}

const showPasswordChangeForm = () => {
    modalTitle.innerHTML = 'Update Password Here..';
    showRightElement('password_change_form_div');
    $('#profileModal').modal('toggle');
}

const delete_account = (event) => {
    // Send a DELETE request to the specific endpoint of the server to delete the users account
    fetch('/users/delete_account', {
        method: 'DELETE',
        headers: {
            'X-CSRFToken': event.target.previousElementSibling.value
        }
    })
        .then(response => {
            console.log(response);
            location.href = '/users/login';
        })
        .catch(error => console.error(error))
}

/* Show the modal with the  appropriate form and error message in the case 
 the user provides an invalid input, like an invalid email or a mismatched password */
if (document.getElementById('error_1_id_username') != null) {
    showUsernameChangeForm()
} else if (document.getElementById('error_1_id_email') != null) {
    showEmailChangeForm();
} else if (document.getElementById('error_1_id_about') != null) {
    showAboutForm();
} else if (document.getElementById('error_1_id_old_password') != null || document.getElementById('error_1_id_new_password2') != null) {
    showPasswordChangeForm();
}

// Prevent the page from reloading once the modal is closed
$('#profileModal').on('hide.bs.modal', (e) => {
    history.pushState(null, '');
})

/* loop over all the edit elements in the HTMLCollection and adds an event listener to each 
once the user clicks on any of them the relevant function is invoked or code implemented */
for (let i = 0; i < pens.length; i++) {
    pens.item(i).addEventListener('click', function () {
        if (this.id === 'username') {
            showUsernameChangeForm()
        }
        else if (this.id === 'pic') {
            const dropDiv = document.createElement('div');
            dropDiv.id = 'drop_div';

            // Utilize DropZone for uploading image using a dropbox
            dropDiv.innerHTML = `
                    <form action="#" method="post" class="dropzone" id="myDropzone" enctype="multipart/form-data">
                        ${document.getElementById('csrf_token').innerHTML}
                        <div class="fallback">
                            <input name="file" type="file"/>
                          </div>
                    </form>
                    <input id="submit_button" type="submit" value="Update" class="btn btn-primary mt-4 form_input">`
            modalTitle.innerHTML = 'Update Profile Picture Here..';

            /* Check if the dropzone element is already in the modal-body
             If not appends it */
            let exists = false;
            for (let i = 0; i < modalBody.children.length; i++) {
                if (modalBody.children[i] === document.getElementById('drop_div')) exists = true;
            }
            if (!exists) modalBody.append(dropDiv);
            showRightElement('drop_div');

            // Create the Dropzone 
            Dropzone.autoDiscover = false;
            const myDropZone = new Dropzone('#myDropzone', {
                url: 'user_profile',
                addRemoveLinks: true,
                method: 'POST',
                params: 'Image upload',
                DictFileTooBig: 'This file exceeds the maximum size',
                clickable: true,
                maxFiles: 1,
                maxFilesize: 50,
                acceptedFiles: '.jpg, .jpeg, .png, .bmp, .gif, .tiff',
                dictDefaultMessage: 'Drop image here',
                autoProcessQueue: false,
                init: function () {
                    document.getElementById('submit_button').onclick = (event) => {
                        event.preventDefault();
                        event.stopPropagation();
                        this.autoProcessQueue = true;
                        this.processQueue();
                    }
                },
                success: function f(response) {
                    console.log(response);
                    location.reload();
                },
            });
        }
        else if (this.id === 'email') {
            showEmailChangeForm()
        }
        else if (this.id === 'about') {
            showAboutForm()
        }
    })
}

document.getElementById('password_update_button').addEventListener('click', () => {
    showPasswordChangeForm()
})

document.getElementById('delete_account_button').addEventListener('click', () => {
    modalTitle.innerHTML = 'Delete Account..';
    showRightElement('delete_prompt');
});

document.getElementById('yes').addEventListener('click', delete_account);
document.getElementById('no').addEventListener('click', () => { $('#profileModal').modal('hide') });
