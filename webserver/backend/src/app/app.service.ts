import * as WebSocket from 'ws';
import { Injectable } from '@nestjs/common';
import { HomecageCommand, DeviceInfo, ResDeviceInfo, RecordingState, DeviceType } from '../../proto/homecage';

interface Ws extends WebSocket {
  id: string
}

@Injectable()
export class AppService {

  public recordingState: RecordingState = RecordingState.STATE_IDLE;

  private deviceInfos: Map<string, DeviceInfo> = new Map<string, DeviceInfo>();
  private rpiWebsockets: Map<string, Ws> = new Map<string, Ws>();
  private webappWebsockets: Map<string, Ws> = new Map<string, Ws>();


  constructor() {}

  public setDeviceInfo(client: Ws, cmd: HomecageCommand) {
    for (const deviceInfo of cmd.resDeviceInfo.deviceInfos) {
      this.deviceInfos.set(client.id, deviceInfo);
      
      if (deviceInfo.deviceType == DeviceType.TYPE_RPI) {
        this.rpiWebsockets.set(client.id, client);
      }

      if (deviceInfo.deviceType == DeviceType.TYPE_WEBAPP) {
        this.webappWebsockets.set(client.id, client);
      }
    }
  }

  public getRpiWebsockets(): Ws[] {
    const websockets: Ws[] = [];

    for (const [key, value] of this.rpiWebsockets.entries()) {
      websockets.push(value);
    }
    return websockets;
  }

  public getWebappWebsockets(): Ws[] {
    const websockets: Ws[] = [];

    for (const [key, value] of this.webappWebsockets.entries()) {
      websockets.push(value);
    }
    return websockets;
  }

  public getDeviceInfo(): ResDeviceInfo {
    const deviceInfos: DeviceInfo[] = [];

    for (const [key, value] of this.deviceInfos.entries()) {
      deviceInfos.push(value);
    }

    return {deviceInfos: deviceInfos}
  }

  public deleteDeviceInfo(id: string) {
    this.deviceInfos.delete(id);
    this.rpiWebsockets.delete(id);
    this.webappWebsockets.delete(id);
  }

}
