/**
 * IndexedDB storage manager for Luminote.
 *
 * This module provides the IndexedDBManager class for client-side storage of
 * translations, history, notes, and artifacts using the browser's IndexedDB API.
 *
 * Related ADR: ADR-003 (Client-Side Storage Strategy)
 */

/**
 * Translation record stored in IndexedDB.
 */
export interface TranslationRecord {
	translation_id: string;
	document_url: string;
	block_id: string;
	source_text: string;
	translated_text: string;
	source_language: string;
	target_language: string;
	provider: string;
	model: string;
	created_at: number;
}

/**
 * History entry stored in IndexedDB.
 */
export interface HistoryEntry {
	history_id: string;
	document_url: string;
	title: string;
	visited_at: number;
	language_pair: string;
	content_preview: string;
	metadata: Record<string, unknown>;
}

/**
 * Note record stored in IndexedDB.
 */
export interface NoteRecord {
	note_id: string;
	document_url: string;
	block_id: string;
	note_type: 'explanation' | 'definition' | 'summary' | 'highlight';
	content: string;
	created_at: number;
	updated_at: number;
	tags: string[];
}

/**
 * Artifact record stored in IndexedDB.
 */
export interface ArtifactRecord {
	artifact_id: string;
	document_url: string;
	job_id: string;
	artifact_type: string;
	content: Record<string, unknown>;
	provider: string;
	model: string;
	prompt_version: string;
	created_at: number;
}

/**
 * IndexedDB database constants.
 */
export const DATABASE_NAME = 'luminote';
export const DATABASE_VERSION = 1;
export const STORE_TRANSLATIONS = 'translations';
export const STORE_HISTORY = 'history';
export const STORE_NOTES = 'notes';
export const STORE_ARTIFACTS = 'artifacts';

/**
 * Custom error for quota exceeded situations.
 */
export class QuotaExceededError extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'QuotaExceededError';
	}
}

/**
 * Custom error for database operations.
 */
export class DatabaseError extends Error {
	constructor(message: string) {
		super(message);
		this.name = 'DatabaseError';
	}
}

/**
 * IndexedDB Manager for Luminote storage.
 *
 * Manages all IndexedDB operations including database initialization,
 * CRUD operations for translations, history, notes, and artifacts,
 * and data lifecycle management.
 */
export class IndexedDBManager {
	private db: IDBDatabase | null = null;
	private initPromise: Promise<void> | null = null;

	/**
	 * Get the initialized database instance.
	 *
	 * @returns Promise resolving to IDBDatabase instance.
	 * @throws DatabaseError if database initialization fails.
	 */
	async getDB(): Promise<IDBDatabase> {
		if (this.db) {
			return this.db;
		}

		// If initialization is in progress, wait for it
		if (this.initPromise) {
			await this.initPromise;
			if (this.db) {
				return this.db;
			}
		}

		// Start initialization
		this.initPromise = this.initializeDB();
		await this.initPromise;

		if (!this.db) {
			throw new DatabaseError('Failed to initialize database');
		}

		return this.db;
	}

	/**
	 * Initialize the IndexedDB database with schema.
	 *
	 * Creates the database with version 1 schema including all object stores
	 * and indexes. Supports version migration for future schema changes.
	 */
	private async initializeDB(): Promise<void> {
		return new Promise((resolve, reject) => {
			const request = indexedDB.open(DATABASE_NAME, DATABASE_VERSION);

			request.onerror = () => {
				reject(new DatabaseError(`Failed to open database: ${request.error?.message}`));
			};

			request.onsuccess = () => {
				this.db = request.result;
				resolve();
			};

			request.onupgradeneeded = (event) => {
				const db = (event.target as IDBOpenDBRequest).result;

				// Version 1: Initial schema
				if (event.oldVersion < 1) {
					// Create translations store
					if (!db.objectStoreNames.contains(STORE_TRANSLATIONS)) {
						const translationsStore = db.createObjectStore(STORE_TRANSLATIONS, {
							keyPath: 'translation_id'
						});
						translationsStore.createIndex('document_url', 'document_url', { unique: false });
						translationsStore.createIndex('created_at', 'created_at', { unique: false });
						translationsStore.createIndex('block_id', 'block_id', { unique: false });
					}

					// Create history store
					if (!db.objectStoreNames.contains(STORE_HISTORY)) {
						const historyStore = db.createObjectStore(STORE_HISTORY, {
							keyPath: 'history_id'
						});
						historyStore.createIndex('document_url', 'document_url', { unique: false });
						historyStore.createIndex('visited_at', 'visited_at', { unique: false });
					}

					// Create notes store
					if (!db.objectStoreNames.contains(STORE_NOTES)) {
						const notesStore = db.createObjectStore(STORE_NOTES, { keyPath: 'note_id' });
						notesStore.createIndex('document_url', 'document_url', { unique: false });
						notesStore.createIndex('created_at', 'created_at', { unique: false });
						notesStore.createIndex('block_id', 'block_id', { unique: false });
					}

					// Create artifacts store
					if (!db.objectStoreNames.contains(STORE_ARTIFACTS)) {
						const artifactsStore = db.createObjectStore(STORE_ARTIFACTS, {
							keyPath: 'artifact_id'
						});
						artifactsStore.createIndex('document_url', 'document_url', { unique: false });
						artifactsStore.createIndex('job_id', 'job_id', { unique: false });
						artifactsStore.createIndex('created_at', 'created_at', { unique: false });
					}
				}

				// Future migrations would go here
				// if (event.oldVersion < 2) { ... }
			};
		});
	}

	/**
	 * Add a translation record to the database.
	 *
	 * @param translation - Translation record to add.
	 * @throws QuotaExceededError if storage quota is exceeded.
	 * @throws DatabaseError if operation fails.
	 */
	async addTranslation(translation: TranslationRecord): Promise<void> {
		const db = await this.getDB();

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_TRANSLATIONS, 'readwrite');
				const store = transaction.objectStore(STORE_TRANSLATIONS);
				const request = store.add(translation);

				request.onsuccess = () => resolve();

				request.onerror = () => {
					if (request.error?.name === 'QuotaExceededError') {
						reject(
							new QuotaExceededError(
								'Storage quota exceeded. Please clear old data or free up space.'
							)
						);
					} else {
						reject(new DatabaseError(`Failed to add translation: ${request.error?.message}`));
					}
				};

				transaction.onerror = () => {
					reject(new DatabaseError(`Transaction failed: ${transaction.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to add translation: ${error}`));
			}
		});
	}

	/**
	 * Get all translations for a specific document URL.
	 *
	 * @param document_url - URL of the document.
	 * @returns Promise resolving to array of translation records.
	 * @throws DatabaseError if operation fails.
	 */
	async getTranslations(document_url: string): Promise<TranslationRecord[]> {
		const db = await this.getDB();

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_TRANSLATIONS, 'readonly');
				const store = transaction.objectStore(STORE_TRANSLATIONS);
				const index = store.index('document_url');
				const request = index.getAll(document_url);

				request.onsuccess = () => {
					resolve(request.result as TranslationRecord[]);
				};

				request.onerror = () => {
					reject(new DatabaseError(`Failed to get translations: ${request.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to get translations: ${error}`));
			}
		});
	}

	/**
	 * Delete a translation by ID.
	 *
	 * @param translation_id - ID of the translation to delete.
	 * @throws DatabaseError if operation fails.
	 */
	async deleteTranslation(translation_id: string): Promise<void> {
		const db = await this.getDB();

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_TRANSLATIONS, 'readwrite');
				const store = transaction.objectStore(STORE_TRANSLATIONS);
				const request = store.delete(translation_id);

				request.onsuccess = () => resolve();

				request.onerror = () => {
					reject(new DatabaseError(`Failed to delete translation: ${request.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to delete translation: ${error}`));
			}
		});
	}

	/**
	 * Add a history entry to the database.
	 *
	 * @param history_entry - History entry to add.
	 * @throws QuotaExceededError if storage quota is exceeded.
	 * @throws DatabaseError if operation fails.
	 */
	async addHistory(history_entry: HistoryEntry): Promise<void> {
		const db = await this.getDB();

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_HISTORY, 'readwrite');
				const store = transaction.objectStore(STORE_HISTORY);
				const request = store.add(history_entry);

				request.onsuccess = () => resolve();

				request.onerror = () => {
					if (request.error?.name === 'QuotaExceededError') {
						reject(
							new QuotaExceededError(
								'Storage quota exceeded. Please clear old history or free up space.'
							)
						);
					} else {
						reject(new DatabaseError(`Failed to add history: ${request.error?.message}`));
					}
				};

				transaction.onerror = () => {
					reject(new DatabaseError(`Transaction failed: ${transaction.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to add history: ${error}`));
			}
		});
	}

	/**
	 * Get all history entries for a specific document URL.
	 *
	 * @param document_url - URL of the document.
	 * @returns Promise resolving to array of history entries.
	 * @throws DatabaseError if operation fails.
	 */
	async getHistory(document_url: string): Promise<HistoryEntry[]> {
		const db = await this.getDB();

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_HISTORY, 'readonly');
				const store = transaction.objectStore(STORE_HISTORY);
				const index = store.index('document_url');
				const request = index.getAll(document_url);

				request.onsuccess = () => {
					resolve(request.result as HistoryEntry[]);
				};

				request.onerror = () => {
					reject(new DatabaseError(`Failed to get history: ${request.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to get history: ${error}`));
			}
		});
	}

	/**
	 * Clear old history entries older than specified number of days.
	 *
	 * @param days - Number of days to keep history (default: 30).
	 * @returns Promise resolving to number of entries deleted.
	 * @throws DatabaseError if operation fails.
	 */
	async clearOldHistory(days: number = 30): Promise<number> {
		const db = await this.getDB();
		const cutoffTime = Date.now() - days * 24 * 60 * 60 * 1000;

		return new Promise((resolve, reject) => {
			try {
				const transaction = db.transaction(STORE_HISTORY, 'readwrite');
				const store = transaction.objectStore(STORE_HISTORY);
				const index = store.index('visited_at');

				// Get all entries older than cutoff
				const range = IDBKeyRange.upperBound(cutoffTime);
				const request = index.openCursor(range);

				let deletedCount = 0;

				request.onsuccess = (event) => {
					const cursor = (event.target as IDBRequest<IDBCursorWithValue>).result;
					if (cursor) {
						cursor.delete();
						deletedCount++;
						cursor.continue();
					} else {
						// No more entries
						resolve(deletedCount);
					}
				};

				request.onerror = () => {
					reject(new DatabaseError(`Failed to clear old history: ${request.error?.message}`));
				};
			} catch (error) {
				reject(new DatabaseError(`Failed to clear old history: ${error}`));
			}
		});
	}

	/**
	 * Close the database connection.
	 * Should be called when the database is no longer needed.
	 */
	close(): void {
		if (this.db) {
			this.db.close();
			this.db = null;
			this.initPromise = null;
		}
	}
}

/**
 * Singleton instance of IndexedDBManager.
 * Use this for all IndexedDB operations in the application.
 */
export const indexedDBManager = new IndexedDBManager();
