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
  sortedDays: DayRead[] = [];
  devices: DeviceConfigRead[] = [];
  selectedDevice: DeviceConfigRead | undefined;
  sortKey: keyof DayRead = 'date';
  sortOrder: 'asc' | 'desc' = 'desc';

  constructor(private dayService: DayService, private deviceService: DeviceService, private modalService: NgbModal) {
    this.deviceService = deviceService;
    this.dayService = dayService;
    this.modalService = modalService;
  }

  ngOnInit(): void {
    this.updateDevices();
    this.updateDays();
  }

  onTableHeaderClick(key: keyof DayRead): void {
    if (this.sortKey === key) {
      this.sortOrder = this.sortOrder === 'asc' ? 'desc' : 'asc';
    } else {
      this.sortKey = key;
      this.sortOrder = 'asc';
    }

    this.sortTable(this.sortKey);
  }

  sortTable(key: keyof DayRead): void {
    this.sortedDays = this.days.sort((a: DayRead, b: DayRead) => {
      const aValue = a[key] as any;
      const bValue = b[key] as any;

      if (aValue < bValue) {
        return this.sortOrder === 'asc' ? -1 : 1;
      }
      if (aValue > bValue) {
        return this.sortOrder === 'asc' ? 1 : -1;
      }
      return 0;
    });
  }

  getSortClass(key: keyof DayRead): string {
    if (this.sortKey !== key) {
      return '';
    }
    return this.sortOrder === 'asc' ? 'bi-arrow-up' : 'bi-arrow-down';
  }

  updateDays() {
    this.dayService.getDays(this.selectedDevice?.name).subscribe((days: DayRead[]) => {
      this.days = days;
      this.sortTable(this.sortKey);
    });
  }

  updateDevices() {
    this.deviceService.getDevices().subscribe((devices: DeviceConfigRead[]) => {
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
        .updateDay(day.id, dayCreate)
        .subscribe((day: DayRead) => { });
      modalRef.close();
      this.updateDays();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }

  onDeleteClick(day: DayRead) {
    this.dayService.deleteDay(day.id).subscribe(() => {
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
        .createDay(dayCreate)
        .subscribe((day: DayRead) => { });
      modalRef.close();
      this.updateDays();
    });

    modalRef.componentInstance.abort.subscribe(() => {
      modalRef.close();
    });
  }
}
