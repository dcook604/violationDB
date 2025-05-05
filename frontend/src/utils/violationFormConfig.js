// Dropdown options
export const BUILDING_OPTIONS = ['Townhouse', 'Apartment'];
export const VIOLATION_CATEGORY_OPTIONS = [
  'Ambulance/Fire Visit', 'Balcony - Items Thrown', 'Balcony - Storage', 'Bike Room Break In',
  'Bike/Rollerblade in Lobby/Elevator', 'Burst Pipe', 'Bylaw Violations', 'Car Break-In',
  'Compactor Problem', 'Damage to Common Area', 'Elevator Issue', 'Garbage Room Issue',
  'Illegal Move', 'Illegal Renovation', 'Improper Garbage/Recycling Disposal',
  'Items in Parking Stall', 'Noise Complaint', 'Parking Violation', 'Locker Break-In', 'Other'
];
export const WHERE_DID_OPTIONS = [
  'Unit', 'Recycle/Garbage Room', 'Parkade', 'Interior Common Area',
  'Exterior Common Area', 'Garden', 'Park'
];
export const SECURITY_POLICE_OPTIONS = ['Security', 'Police'];
export const FINE_LEVIED_OPTIONS = ['$50.00', '$100.00', '$200.00', '$1000.00', 'No Fine'];
export const STATUS_OPTIONS = [
  'Open',
  'Closed-No Fine Issued',
  'Closed-Fines Issued',
  'Pending Owner Response',
  'Pending Council Response',
  'Reject'
];

export const FILE_ACCEPT = '.pdf,.doc,.docx,.xls,.xlsx,.csv,.txt,.rtf,.html,.zip,.mp3,.wma,.mpg,.flv,.avi,.jpg,.jpeg,.png,.gif';
export const MAX_FILES = 5;
export const MAX_FILE_SIZE_MB = 10;

// Validation functions
export function isValidEmail(email) {
  return /^[^\s@]+@[^\s@]+\.[^\s@]+$/.test(email);
}
export function isValidPhone(phone) {
  // Accept (000) 000-0000 or 000-000-0000
  return /^(\(\d{3}\) \d{3}-\d{4}|\d{3}-\d{3}-\d{4})$/.test(phone);
} 