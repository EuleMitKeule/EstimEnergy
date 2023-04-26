import { Component } from '@angular/core';
import { DeviceConfigRead, DeviceService } from '../api';

@Component({
  selector: 'app-energy-page',
  templateUrl: './energy-page.component.html',
  styleUrls: ['./energy-page.component.css']
})
export class EnergyPageComponent {
  devices: DeviceConfigRead[] = [];
  selectedDevice: DeviceConfigRead | undefined;

  constructor(private deviceService: DeviceService) { }

  ngOnInit(): void {
    this.updateDevices();
  }

  updateDevices() {
    this.deviceService.getDevices().subscribe((devices: DeviceConfigRead[]) => {
      this.devices = devices;
    });
  }

  onSelectDevice(device: DeviceConfigRead | undefined) {
    this.selectedDevice = device;
  }
}
