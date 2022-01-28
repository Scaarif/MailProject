like = document.querySelectorAll(".liked");

edit = document.querySelectorAll(".edit");
text_area = document.querySelectorAll(".textarea");

like.forEach((element) => {
	like_handler(element);
});

edit.forEach((element) => {
	element.addEventListener("click", () => {
		edit_handler(element);
	});
});

text_area.forEach((element) => {
	element.addEventListener("keyup", (e) => {
		if (e.keyCode == 13 && e.shiftKey) return;
		if (e.keyCode ===13) edit_handler(element);
	});
});

function edit_post(id, post) {
	form = new FormData();
	form.append("id", id);
	form.append("post", post.trim());

	fetch("/editpost/", {
		method: "POST",
		body: form,
	}).then((res) => {
		document.querySelector(`#post-content-${id}`).textContent = post; 
		document.querySelector(`#post-content-${id}`).style.display = "block"; //redisplay the post
		document.querySelector(`#post-edit-${id}`).style.display = "none";//hide the edit textarea...
		document.querySelector(`#post-edit-${id}`).value = post.trim();
	});
}

function edit_handler(element) {
	id = element.getAttribute("data-id"); //both edit btn and textarea share an id
	edit_btn = document.querySelector(`#edit-btn-${id}`);
	if (edit_btn.textContent == "Edit") {
		document.querySelector(`#post-content-${id}`).style.display = "none"; //dont display the post itself
		document.querySelector(`#post-edit-${id}`).style.display = "block"; //display the textarea prefilled with post
		edit_btn.textContent = "Save";
		edit_btn.setAttribute("class", "text-success edit");	
	} else if (edit_btn.textContent == "Save") {
		edit_post(id, document.querySelector(`#post-edit-${id}`).value);

		edit_btn.textContent = "Edit";
		edit_btn.setAttribute("class", "text-primary edit");
	}
}

function like_handler(element) {
	element.addEventListener("click", () => {
		id = element.getAttribute("data-id");
		is_liked = element.getAttribute("data-is_liked");
		icon = document.querySelector(`#post-like-${id}`);
		count = document.querySelector(`#post-count-${id}`);

		form = new FormData();
		form.append("id", id);
		form.append("is_liked", is_liked);
		fetch("/like/", {
			method: "POST",
			body: form,
		})
		.then((res) => res.json())
		.then((res) => {
			if (res.status == 201) {
				if (res.is_liked === "yes") {
					icon.src = "https://img.icons8.com/plasticine/100/000000/like.png";
					element.setAttribute("data-is_liked", "yes");
				} else {
					icon.src = "https://img.icons8.com/plasticine/100/000000/like--v2.png";
					element.setAttribute("data-is_liked", "no");
				}
				count.textContent = res.likes;
			}
		})
		.catch(function (res) {
			alert("Netwrk Error. Please Check your connection");
		});
	});
}