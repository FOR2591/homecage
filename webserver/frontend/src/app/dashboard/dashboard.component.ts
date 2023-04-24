import { Component } from '@angular/core';
import { Commands, DeviceInfo, DeviceType, HomecageCommand } from 'proto/homecage';
import { BackendService } from '../backend/backend.service';

@Component({
  selector: 'hc-dashboard',
  templateUrl: './dashboard.component.html',
  styleUrls: ['./dashboard.component.scss']
})
export class DashboardComponent {

  public deviceInfo: DeviceInfo[]  = [];

  constructor(private backend: BackendService) {
    this.backend.on_open.subscribe(this._on_connect.bind(this));
    this.backend.on_message.subscribe(this._on_message.bind(this));
  }

  private _on_connect() {
    this.backend.request_device_info();
    // this.backend.getRecordingState();
  }

  private _on_message(msg: HomecageCommand) {
    switch(msg.command) {
      case Commands.CMD_RES_DEVICE_INFO:
        this.deviceInfo = [];

        for (const deviceInfo of msg.resDeviceInfo!.deviceInfos) {
          if(deviceInfo.deviceType == DeviceType.TYPE_RPI) {this.deviceInfo.push(deviceInfo)};
        }
        break;  
    }
  }


}
