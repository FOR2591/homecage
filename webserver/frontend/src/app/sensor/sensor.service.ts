import { Injectable } from "@angular/core";
import { Commands, HomecageCommand, RecordingState } from "proto/homecage";
import { BackendService } from "../backend/backend.service";

@Injectable({providedIn: 'root'})
export class SensorService {

    public recordingState: RecordingState = RecordingState.STATE_EMPTY;

    constructor(private backend: BackendService) { 
        this.backend.on_message.subscribe(this.onMessage.bind(this))
        console.log('register')
    }

    private onMessage(msg: HomecageCommand) {
        switch(msg.command) {
          case Commands.CMD_RES_GET_RECORDING_STATE:
            console.log(msg.resGetRecordingState)
            this.recordingState = msg.resGetRecordingState!.state;
            break;
        }
      }
}