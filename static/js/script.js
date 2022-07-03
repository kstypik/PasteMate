dayjs.extend(window.dayjs_plugin_relativeTime)
const toRelativeDateTimes = document.getElementsByClassName("to-relative-datetime");
for (const dtElement of toRelativeDateTimes) {
    let relativeDatetime = dayjs().to(dayjs(dtElement.innerHTML));
    dtElement.innerHTML = relativeDatetime;
}

