dayjs.extend(window.dayjs_plugin_relativeTime)
const toRelativeDateTimes = document.getElementsByClassName("to-relative-datetime");
for (const dtElement of toRelativeDateTimes) {
    let relativeDatetime = dayjs().to(dayjs(dtElement.innerHTML));
    dtElement.innerHTML = relativeDatetime;
}

let getCopyHandler = (element, content, position) => {
    let hasCopied = false;
    handleCopy = (event) => {
      event.preventDefault();
      
      

      content.select();
      content.setSelectionRange(0, 99999);
      navigator.clipboard.writeText(content.value);
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