import { Component, OnInit } from '@angular/core';
import { Commands, HomecageCommand, RecordingState } from 'proto/homecage';
import { BackendService } from '../backend/backend.service';

@Component({
  selector: 'hc-controls',
  templateUrl: './controls.component.html',
  styleUrls: ['./controls.component.scss']
})
export class ControlsComponent implements OnInit {

  state: RecordingState = RecordingState.STATE_IDLE;

  constructor(private backend: BackendService) {
    this.backend.on_open.subscribe(this._onConnect.bind(this));
    this.backend.on_message.subscribe(this._onMessage.bind(this));
  }

  ngOnInit(): void {
  }

  public toggleRecordingState() {
    if (this.state == RecordingState.STATE_IDLE) {
      this.state = RecordingState.STATE_RECORDING;
      this.backend.setRecordingState(RecordingState.STATE_RECORDING);
    } else {
      this.state = RecordingState.STATE_IDLE;
      this.backend.setRecordingState(RecordingState.STATE_IDLE);
    }
  }

  private _onConnect() {
    this.backend.getRecordingState();
  }

  private _onMessage(msg: HomecageCommand) {
    switch(msg.command) {
      case Commands.CMD_RES_GET_RECORDING_STATE:
        this.state = msg.resGetRecordingState!.state;
        break;
    }
  }

}
