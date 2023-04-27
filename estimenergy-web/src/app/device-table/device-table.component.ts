import { Component } from '@angular/core';
import { DeviceConfig, DeviceConfigRead, DeviceService } from '../api';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DeviceModalComponent } from '../device-modal/device-modal.component';

@Component({
  selector: 'app-device-table',
  templateUrl: './device-table.component.html',
  styleUrls: ['./device-table.component.css']
})
export class DeviceTableComponent {

  devices: DeviceConfigRead[] = [];

  constructor(private deviceService: DeviceService, private modalService: NgbModal) { }

  ngOnInit(): void {
    this.updateDevices();
  }

  updateDevices() {
    this.deviceService.getDevices().subscribe((devices: DeviceConfigRead[]) => {
      this.devices = devices;
    });
  }

  onEditClick(device: DeviceConfigRead) {
    const modalRef = this.modalService.open(DeviceModalComponent);
    modalRef.componentInstance.modalTitle = 'Edit Device';
    modalRef.componentInstance.displaySecrets = false;
    modalRef.componentInstance.deviceConfig = {
      name: device.name,
      type: device.type,
      cost_per_kwh: device.cost_per_kwh,
      base_cost_per_month: device.base_cost_per_month,
      payment_per_month: device.payment_per_month,
      billing_month: device.billing_month,
      min_accuracy: device.min_accuracy,
    };

    modalRef.componentInstance.save.subscribe((deviceConfig: DeviceConfig) => {
      if (device.name === undefined) {
        return;
      }

      this.deviceService.updateDevice(device.name, deviceConfig).subscribe(() => {
        this.updateDevices();
      });

      modalRef.close();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }

  onDeleteClick(device: DeviceConfigRead) {
    if (device.name === undefined) {
      return;
    }

    this.deviceService.deleteDevice(device.name).subscribe(() => {
      this.updateDevices();
    });
  }

  onStartClick(device: DeviceConfigRead) {
    if (device.name === undefined) {
      return;
    }

    this.deviceService.startDevice(device.name).subscribe(() => {
      this.updateDevices();
    });
  }

  onStopClick(device: DeviceConfigRead) {
    if (device.name === undefined) {
      return;
    }

    this.deviceService.stopDevice(device.name).subscribe(() => {
      this.updateDevices();
    });
  }

  onCreateClick() {
    const modalRef = this.modalService.open(DeviceModalComponent);
    modalRef.componentInstance.modalTitle = 'Create Device';
    modalRef.componentInstance.displaySecrets = true;
    modalRef.componentInstance.deviceConfig = {
      name: '',
      type: 'glow',
      host: 'localhost',
      port: 6053,
      password: '',
      cost_per_kwh: 0.0,
      base_cost_per_month: 0.0,
      payment_per_month: 0.0,
      billing_month: 1,
      min_accuracy: 0.0,
    };

    modalRef.componentInstance.save.subscribe((deviceConfig: DeviceConfig) => {
      this.deviceService.createDevice(deviceConfig).subscribe({
        next: () => {
          this.updateDevices();
        },
        error: (err) => {
          this.updateDevices();
        }
      });

      modalRef.close();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }
}
