const BASE_URL = "http://127.0.0.1:5000"

$(".messages-like").on("click", async function (evt) {
    evt.preventDefault();
  
    const $targ = $(evt.target);
	const $closestLi = $targ.closest('li');
	const msgId = $closestLi.attr('id');

    const likeBtn = document.getElementById(`like-button-${msgId}`);

    fetch(`${BASE_URL}/messages/${msgId}/like`, {method: 'POST'}).then((res) => 
    res.json()).then((data) => {
        if (data['liked'] === true) {
            likeBtn.className = "btn btn-sm btn-primary";
        } else {
            likeBtn.className = "btn btn-sm btn-secondary";
        }
    }).catch((e) => alert('Could not like post.'));
  });
