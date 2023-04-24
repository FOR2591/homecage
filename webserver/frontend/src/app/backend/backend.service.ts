import { Injectable } from "@angular/core";

import { Subject } from "rxjs";
import { webSocket, WebSocketSubject } from 'rxjs/webSocket';

import { v4 as uuidv4 } from 'uuid';

import { HomecageCommand, Commands, RecordingState, ReqSetRecordingState, DeviceType } from "proto/homecage";


@Injectable({providedIn: 'root'})
export class BackendService {

    public on_message: Subject<HomecageCommand> = new Subject<HomecageCommand>();
    public on_open: Subject<void> = new Subject<void>();
    public on_close: Subject<void> = new Subject<void>();
    
    private _ws!: WebSocketSubject<any>;
    private _clientName: string = uuidv4();

    constructor() {
        // this._ws = webSocket({url: `ws://${window.location.host}`, openObserver: { next: () => {this.on_open.next()} }});
        this._ws = webSocket({url: `ws://homecage2:3000`, openObserver: { next: () => {this.on_open.next()} }});
        console.log(this._ws)
        //
        this.on_open.subscribe(this.send_device_info.bind(this));

        //
        this._ws.subscribe({
            next: this._on_message.bind(this),
            error: (err) => {},
            complete: this._on_close.bind(this)
        });
    }

    public request_device_info() {
        const cmd : HomecageCommand = {
            clientName: "blub",
            command: Commands.CMD_REQ_DEVICE_INFO
        }

        this.send_command(cmd);
    }

    public getRecordingState() {
        const cmd: HomecageCommand = {
            clientName: "Webapp",
            command: Commands.CMD_REQ_GET_RECORDING_STATE,
        }

        this.send_command(cmd);
    }

    public setRecordingState(state: RecordingState) {
        const cmd : HomecageCommand = {
            clientName: this._clientName,
            command: Commands.CMD_REQ_SET_RECORDING_STATE,
            reqSetRecordingState: { state: state}
        }

        this.send_command(cmd);
    }

    public send_command(cmd: HomecageCommand) {
        this._ws.next({event: 'msg', data: JSON.stringify(HomecageCommand.toJSON(cmd))});
    }

    public send_device_info() {
        const cmd: HomecageCommand = {
            clientName: this._clientName,
            command: Commands.CMD_RES_DEVICE_INFO,
            resDeviceInfo: {
                deviceInfos: [{
                    deviceName: this._clientName,
                    deviceType: DeviceType.TYPE_WEBAPP,
                    cameras: []
                }]
            }
        }

        this.send_command(cmd);
    }

    private _on_message(buffer: {event: 'msg', data: string}) {
        const msg = HomecageCommand.fromJSON(JSON.parse(buffer.data));

        this.on_message.next(msg);

        console.log(msg)
    }

    private _on_close() {
        this.on_close.next();
    }


}