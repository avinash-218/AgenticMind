from random import randint
from pydantic import BaseModel
from crewai.flow import Flow, listen, start
import whisper
from src.meeting_minutes.crews.meeting_minutes_crew.meeting_minutes_crew import MeetingMinutesCrew

class MeetingMinutesState(BaseModel):
    transcript: str = ""
    meeting_minutes: str = ""

class MeetingMinutesFlow(Flow[MeetingMinutesState]):

    @start()
    def transcribe_meeting(self):
        print('Generating transcription...')
        model = whisper.load_model("turbo")
        result = model.transcribe("./harvard.wav")
        full_transcription = result['text']
        self.state.transcript = full_transcription
        print('Transcription:\n', self.state.transcript)

    @listen(transcribe_meeting)
    def create_meeting_minutes(self):
        print('Generating meeting minutes')
        crew = MeetingMinutesCrew()

        inputs = {"transcript": self.state.transcript}
        self.state.meeting_minutes = crew.crew().kickoff(inputs)
        print('Meeting minutes:\n', self.state.meeting_minutes)

def kickoff():
    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.kickoff()


def plot():
    meeting_minutes_flow = MeetingMinutesFlow()
    meeting_minutes_flow.plot()

if __name__ == "__main__":
    kickoff()
