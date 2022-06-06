let toolbarCopy = document.querySelector(".toolbar-copy");
let rawCopy = document.querySelector(".raw-copy");
let rawCode = document.querySelector(".raw-paste-data");

getCopyHandler = (element, position) => {
    handleCopy = (event) => {
      event.preventDefault();
      navigator.clipboard.writeText(rawCode.innerHTML);
      successMsgSpan = document.createElement("span");
      successMsgSpan.innerHTML = "Copied";
      successMsgSpan.classList.add("text-success");
      successMsgSpan.classList.add("mx-2");
      element.insertAdjacentElement(position, successMsgSpan);
      setTimeout(() => {
        successMsgSpan.remove();
      }, 2000);
    }
    return handleCopy;
}
toolbarCopy.addEventListener("click", getCopyHandler(toolbarCopy, "beforebegin"));
rawCopy.addEventListener("click", getCopyHandler(rawCopy, "afterend"));
