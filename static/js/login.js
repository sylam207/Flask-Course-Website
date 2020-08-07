const inputs = document.querySelectorAll(".input");

function addcl(){
	var parent = this.parentNode.parentNode;
	parent.classList.add("focus");
}

function remcl(){
	var parent = this.parentNode.parentNode;
	if(this.value == ""){
		parent.classList.remove("focus");
	}
}

inputs.forEach(input => {
	input.addEventListener("focus", addcl);
	input.addEventListener("blur", remcl);
});
