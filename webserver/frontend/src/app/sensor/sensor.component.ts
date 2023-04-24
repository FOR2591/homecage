import { ChangeDetectorRef, Component, Input, OnDestroy, OnInit } from '@angular/core';
import { Commands, HomecageCommand, RecordingMode, RecordingState, RecordingStatus } from 'proto/homecage';
import { BackendService } from '../backend/backend.service';
import { SensorService } from './sensor.service';

@Component({
  selector: 'hc-sensor',
  templateUrl: './sensor.component.html',
  styleUrls: ['./sensor.component.scss']
})
export class SensorComponent implements OnInit, OnDestroy {

  @Input() public cam = {type: 'Lepton', mode: RecordingMode.UNRECOGNIZED, state: RecordingState.UNRECOGNIZED, status: RecordingStatus.UNRECOGNIZED, shedule: 0}

  public remainingSeconds = 0;

  private interval: any;

  constructor(private sensorService: SensorService) { 
    this.interval = setTimeout(this.count.bind(this), 1000);
  }

  public get recordingMode(): string {
    if(this.cam.mode == RecordingMode.MODE_CONTINOUS) return 'continuous';
    if(this.cam.mode == RecordingMode.MODE_INTERVAL) return 'interval';

    return '';
  }

  public get recordingState(): string {
    if(this.cam.state == RecordingState.STATE_IDLE) return 'idle';
    if(this.cam.state == RecordingState.STATE_RECORDING) return 'recording';
    if(this.cam.state == RecordingState.STATE_WAITING) return 'waiting';
    if(this.cam.state == RecordingState.STATE_ERROR) return 'error';

    return '';
  }

  public get recordingStatus(): string {
    if(this.cam.status == RecordingStatus.STATUS_READY && this.sensorService.recordingState == RecordingState.STATE_IDLE) return 'idle';
    if(this.cam.status == RecordingStatus.STATUS_READY && this.sensorService.recordingState  == RecordingState.STATE_RECORDING){
      if(this.remainingSeconds > 0) {
        return `next recording in ${this.remainingSeconds}`;
      } else {
        return "starting recording ..."
      }
    }
    if(this.cam.status == RecordingStatus.STATUS_WAITING) return 'writing data to disk';
    if(this.cam.status == RecordingStatus.STATUS_RECORDING) return 'recording';
    if(this.cam.status == RecordingStatus.STATUS_ERROR) return 'error';

    return '';
  }

  ngOnInit(): void {
  }

  ngOnDestroy(): void {
    clearTimeout(this.interval);
  }

  private count() {
    this.remainingSeconds = Math.max(Math.floor(this.cam.shedule - (Date.now() / 1000)), 0);
    this.interval = setTimeout(this.count.bind(this), 1000);

  }

}
