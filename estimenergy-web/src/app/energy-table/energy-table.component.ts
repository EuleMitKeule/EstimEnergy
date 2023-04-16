import { Component } from '@angular/core';
import { NgbModal } from '@ng-bootstrap/ng-bootstrap';
import { DayCreate, DayRead, DayService, DeviceConfigRead, DeviceService } from '../api';
import { DayModalComponent } from '../day-modal/day-modal.component';

@Component({
  selector: 'app-energy-table',
  templateUrl: './energy-table.component.html',
  styleUrls: ['./energy-table.component.css'],
})
export class EnergyTableComponent {
  days: DayRead[] = [];
  devices: DeviceConfigRead[] = [];
  selectedDevice: DeviceConfigRead | undefined;

  constructor(private dayService: DayService, private deviceService: DeviceService, private modalService: NgbModal) {
    this.deviceService = deviceService;
    this.dayService = dayService;
    this.modalService = modalService;
  }

  ngOnInit(): void {
    this.updateDevices();
    this.updateDays();
  }

  updateDays() {
    this.dayService.getDaysDayGet(this.selectedDevice?.name).subscribe((days: DayRead[]) => {
      this.days = days;
    });
  }

  updateDevices() {
    this.deviceService.getDevicesDeviceGet().subscribe((devices: DeviceConfigRead[]) => {
      this.devices = devices;
    });
  }

  onSelectDevice(device: DeviceConfigRead) {
    this.selectedDevice = device;
    this.updateDays();
  }

  onEditClick(day: DayRead) {

    const modalRef = this.modalService.open(DayModalComponent);
    modalRef.componentInstance.modalTitle = 'Edit Day';
    modalRef.componentInstance.device = day.device_name;
    modalRef.componentInstance.dayCreate = {
      device_name: day.device_name,
      date: day.date,
      energy: day.energy,
      accuracy: day.accuracy,
    };

    modalRef.componentInstance.save.subscribe((dayCreate: DayCreate) => {
      this.dayService
        .updateDayDayDayIdPut(day.id, dayCreate)
        .subscribe((day: DayRead) => { });
      modalRef.close();
      this.updateDays();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }

  onDeleteClick(day: DayRead) {
    this.dayService.deleteDayDayDayIdDelete(day.id).subscribe(() => {
      this.updateDays();
    });
  }

  onCreateClick() {
    if (!this.selectedDevice) {
      return;
    }

    const modalRef = this.modalService.open(DayModalComponent);
    modalRef.componentInstance.modalTitle = 'Create Day';
    modalRef.componentInstance.device = this.selectedDevice.name;

    modalRef.componentInstance.save.subscribe((dayCreate: DayCreate) => {
      this.dayService
        .createDayDayPost(dayCreate)
        .subscribe((day: DayRead) => { });
      modalRef.close();
      this.updateDays();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }
}
