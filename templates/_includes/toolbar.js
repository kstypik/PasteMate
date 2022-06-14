let toolbarCopy = document.querySelector(".toolbar-copy");
let rawCopy = document.querySelector(".raw-copy");
let rawCode = document.querySelector(".raw-paste-data");

let hasCopied = false;

getCopyHandler = (element, position) => {
    handleCopy = (event) => {
      event.preventDefault();
      
      rawCode.select();
      rawCode.setSelectionRange(0, 99999);
      navigator.clipboard.writeText(rawCode.value);
      // rawCopy.focus();
      

      if (!hasCopied) {
        successMsgSpan = document.createElement("span");
        successMsgSpan.innerHTML = "Copied";
        successMsgSpan.classList.add("text-success");
        successMsgSpan.classList.add("mx-2");
  
        element.insertAdjacentElement(position, successMsgSpan);
      }
      hasCopied = true;
      setTimeout(() => {
        successMsgSpan.remove();
        hasCopied = false;
      }, 2000);
    }
    return handleCopy;
}
toolbarCopy.addEventListener("click", getCopyHandler(toolbarCopy, "beforebegin"));
rawCopy.addEventListener("click", getCopyHandler(rawCopy, "afterend"));
