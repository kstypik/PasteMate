dayjs.extend(window.dayjs_plugin_relativeTime);
const toRelativeDateTimes = document.getElementsByClassName(
	"to-relative-datetime",
);
for (const dtElement of toRelativeDateTimes) {
	const relativeDatetime = dayjs().to(dayjs(dtElement.innerHTML));
	dtElement.innerHTML = relativeDatetime;
}

const getCopyHandler = (element, content, position) => {
	let hasCopied = false;
	let currentSuccessSpan = null;

	handleCopy = (event) => {
		event.preventDefault();

		content.select();
		content.setSelectionRange(0, 99999);
		navigator.clipboard.writeText(content.value);

		if (!hasCopied) {
			hasCopied = true;
			if (currentSuccessSpan) {
				currentSuccessSpan.remove();
			}

			successMsgSpan = document.createElement("span");
			successMsgSpan.innerHTML = "Copied";
			successMsgSpan.classList.add("text-success");
			successMsgSpan.classList.add("mx-2");

			currentSuccessSpan = successMsgSpan;
			element.insertAdjacentElement(position, successMsgSpan);
		}
		setTimeout(() => {
			if (currentSuccessSpan) {
				currentSuccessSpan.remove();
			}
			hasCopied = false;
			currentSuccessSpan = null;
		}, 2000);
	};
	return handleCopy;
};
