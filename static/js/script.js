const toRelativeDateTimes = document.getElementsByClassName("to-relative-datetime");
for (const dtElement of toRelativeDateTimes) {
    relativeDatetime = luxon.DateTime.fromISO(dtElement.innerHTML).setLocale("en").toRelativeCalendar();
    dtElement.innerHTML = relativeDatetime;
}