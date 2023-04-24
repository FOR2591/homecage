import * as WebSocket from 'ws';
import { v4 as uuidv4 } from 'uuid';
import { Logger  } from '@nestjs/common';
import { SubscribeMessage, WebSocketGateway, OnGatewayInit, WebSocketServer, OnGatewayConnection, OnGatewayDisconnect} from '@nestjs/websockets';
import { HomecageCommand, Commands, RecordingState, ResGetRecordingState } from '../../proto/homecage';
import { AppService } from './app.service';

interface Ws extends WebSocket {
    id: string
}

@WebSocketGateway()
export class AppGateway implements OnGatewayInit, OnGatewayConnection, OnGatewayDisconnect {
    
    activeClients: Map<string, Ws> = new Map<string, Ws>();

    private readonly logger = new Logger(AppGateway.name);

    constructor(private appService: AppService) {
    }

    @WebSocketServer() server: WebSocket.Server;

    @SubscribeMessage('msg')
    handleMessage(client: Ws, payload: string): void {
        const msg = HomecageCommand.fromJSON(JSON.parse(payload))

        switch(msg.command) {
            case Commands.CMD_RES_DEVICE_INFO:
                this.appService.setDeviceInfo(client, msg);
                this.sendDeviceInfosToWebapp();
                break;

            case Commands.CMD_REQ_DEVICE_INFO:
                const resDeviceInfo = this.appService.getDeviceInfo();
                this.sendCommand(client, {clientName: "Webserver", command: Commands.CMD_RES_DEVICE_INFO, resDeviceInfo: resDeviceInfo});
                break;

            case Commands.CMD_REQ_SET_RECORDING_STATE:
                this.appService.recordingState = msg.reqSetRecordingState.state;
                this.setRecordingState(msg.reqSetRecordingState.state);
                console.log(this.appService.recordingState);
                break;

            case Commands.CMD_REQ_GET_RECORDING_STATE:
                const recordingState: ResGetRecordingState = {state: this.appService.recordingState};
                this.sendCommand(client, {clientName: "Webserver", command: Commands.CMD_RES_GET_RECORDING_STATE, resGetRecordingState: recordingState});
                break;
        }
    }

    sendCommand(client: Ws, cmd: HomecageCommand) {
        const msg = {event: 'msg', data: JSON.stringify(HomecageCommand.toJSON(cmd))};

        client.send(JSON.stringify(msg));
    }

    sendToWebapp(cmd: HomecageCommand) {
        for (const client of this.appService.getWebappWebsockets()) {
            this.sendCommand(client, cmd);
        }
    }

    afterInit(server: WebSocket.Server) {
    //   this.logger.log('Init');
    }

    sendDeviceInfosToWebapp() {
        const resDeviceInfo = this.appService.getDeviceInfo();
        const cmd: HomecageCommand = {
            clientName: "Webserver", 
            command: Commands.CMD_RES_DEVICE_INFO, 
            resDeviceInfo: resDeviceInfo
        };
        this.sendToWebapp(cmd);
    }
    

    setRecordingState(state: RecordingState) {
        const msg: HomecageCommand = {
            clientName: "Webserver",
            command: Commands.CMD_REQ_SET_RECORDING_STATE,
            reqSetRecordingState: {state: state}
        };

        for (const client of this.appService.getRpiWebsockets()) {
            this.sendCommand(client, msg);
        }

        for(const client of this.appService.getWebappWebsockets()) {
            this.sendCommand(client, {clientName: "Webserver", command: Commands.CMD_RES_GET_RECORDING_STATE, resGetRecordingState: {state: this.appService.recordingState}});
        }
    }

    handleDisconnect(client: Ws) {
        this.appService.deleteDeviceInfo(client.id);
        this.activeClients.delete(client.id);

        this.sendDeviceInfosToWebapp();

        this.logger.log(`Client disconnected: ${client.id}`);
    }

    handleConnection(client: Ws, ...args: any[]) {
        client.id = uuidv4();
        this.activeClients.set(client.id, client);
        this.logger.log(`Client connected: ${client.id}`);
    }
}