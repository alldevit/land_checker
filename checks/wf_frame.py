def wf_frame(self):
    if self.wf_frame_num:
        self.logBad('на ленде wf-фрейм, оставшиеся проверки отменены')
        return True
    else:
        return False