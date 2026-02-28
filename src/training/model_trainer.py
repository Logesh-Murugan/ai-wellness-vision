#!/usr/bin/env python3
"""
Advanced Model Training System for CNN Health Analysis
"""

import tensorflow as tf
import numpy as np
from pathlib import Path
import logging
from typing import Dict, List, Tuple, Optional
import json
from datetime import datetime
import matplotlib.pyplot as plt
from sklearn.metrics import classification_report, confusion_matrix
import seaborn as sns

logger = logging.getLogger(__name__)

class AdvancedModelTrainer:
    """Advanced training system for health analysis CNN models"""
    
    def __init__(self, model_type: str, data_dir: str = "data"):
        self.model_type = model_type
        self.data_dir = Path(data_dir)
        self.model = None
        self.history = None
        
        # Training configuration
        self.config = {
            'batch_size': 32,
            'epochs': 50,
            'learning_rate': 0.001,
            'validation_split': 0.2,
            'early_stopping_patience': 10,
            'reduce_lr_patience': 5,
            'augmentation': True
        }
        
        # Model architectures for different health analysis types
        self.architectures = {
            'skin': self._create_skin_model,
            'eye': self._create_eye_model,
            'food': self._create_food_model,
            'general': self._create_general_model
        }
        
        # Class mappings
        self.class_mappings = {
            'skin': ['healthy', 'acne', 'eczema', 'rash', 'dry_skin', 'oily_skin'],
            'eye': ['healthy', 'red_eye', 'dark_circles', 'puffy', 'tired'],
            'food': ['healthy', 'processed', 'high_calorie', 'low_nutrition', 'balanced'],
            'general': ['normal', 'concerning', 'requires_attention']
        }
    
    def prepare_data(self) -> Tuple[tf.data.Dataset, tf.data.Dataset]:
        """Prepare training and validation datasets"""
        
        train_dir = self.data_dir / 'training' / self.model_type
        val_dir = self.data_dir / 'validation' / self.model_type
        
        if not train_dir.exists() or not val_dir.exists():
            raise ValueError(f"Training data not found for {self.model_type}")
        
        # Data augmentation for training
        if self.config['augmentation']:
            train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(
                rescale=1./255,
                rotation_range=20,
                width_shift_range=0.2,
                height_shift_range=0.2,
                horizontal_flip=True,
                zoom_range=0.2,
                brightness_range=[0.8, 1.2],
                fill_mode='nearest'
            )
        else:
            train_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
        
        # Validation data (no augmentation)
        val_datagen = tf.keras.preprocessing.image.ImageDataGenerator(rescale=1./255)
        
        # Create datasets
        train_dataset = train_datagen.flow_from_directory(
            train_dir,
            target_size=(224, 224),
            batch_size=self.config['batch_size'],
            class_mode='categorical',
            classes=self.class_mappings[self.model_type]
        )
        
        val_dataset = val_datagen.flow_from_directory(
            val_dir,
            target_size=(224, 224),
            batch_size=self.config['batch_size'],
            class_mode='categorical',
            classes=self.class_mappings[self.model_type]
        )
        
        return train_dataset, val_dataset
    
    def _create_skin_model(self, num_classes: int) -> tf.keras.Model:
        """Create specialized CNN model for skin analysis"""
        
        model = tf.keras.Sequential([
            # Input layer
            tf.keras.layers.Input(shape=(224, 224, 3)),
            
            # Feature extraction layers
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            # Attention mechanism for skin features
            tf.keras.layers.Conv2D(256, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.GlobalAveragePooling2D(),
            
            # Classification layers
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def _create_eye_model(self, num_classes: int) -> tf.keras.Model:
        """Create specialized CNN model for eye analysis"""
        
        # Similar architecture but optimized for eye features
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            
            # Fine-grained feature extraction for eye details
            tf.keras.layers.Conv2D(16, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.2),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.3),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.GlobalAveragePooling2D(),
            
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def _create_food_model(self, num_classes: int) -> tf.keras.Model:
        """Create specialized CNN model for food analysis"""
        
        # Architecture optimized for food texture and color analysis
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            
            # Color and texture feature extraction
            tf.keras.layers.Conv2D(32, (5, 5), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.GlobalAveragePooling2D(),
            
            tf.keras.layers.Dense(512, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def _create_general_model(self, num_classes: int) -> tf.keras.Model:
        """Create general-purpose CNN model"""
        
        model = tf.keras.Sequential([
            tf.keras.layers.Input(shape=(224, 224, 3)),
            
            tf.keras.layers.Conv2D(32, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(64, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.MaxPooling2D((2, 2)),
            tf.keras.layers.Dropout(0.25),
            
            tf.keras.layers.Conv2D(128, (3, 3), activation='relu', padding='same'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.GlobalAveragePooling2D(),
            
            tf.keras.layers.Dense(256, activation='relu'),
            tf.keras.layers.BatchNormalization(),
            tf.keras.layers.Dropout(0.5),
            
            tf.keras.layers.Dense(num_classes, activation='softmax')
        ])
        
        return model
    
    def create_model(self) -> tf.keras.Model:
        """Create model based on type"""
        
        num_classes = len(self.class_mappings[self.model_type])
        
        if self.model_type in self.architectures:
            model = self.architectures[self.model_type](num_classes)
        else:
            model = self._create_general_model(num_classes)
        
        # Compile model
        model.compile(
            optimizer=tf.keras.optimizers.Adam(learning_rate=self.config['learning_rate']),
            loss='categorical_crossentropy',
            metrics=['accuracy', 'precision', 'recall']
        )
        
        self.model = model
        return model
    
    def train_model(self, train_dataset, val_dataset) -> Dict:
        """Train the model with advanced techniques"""
        
        if self.model is None:
            self.create_model()
        
        # Callbacks
        callbacks = [
            tf.keras.callbacks.EarlyStopping(
                monitor='val_loss',
                patience=self.config['early_stopping_patience'],
                restore_best_weights=True
            ),
            tf.keras.callbacks.ReduceLROnPlateau(
                monitor='val_loss',
                factor=0.2,
                patience=self.config['reduce_lr_patience'],
                min_lr=1e-7
            ),
            tf.keras.callbacks.ModelCheckpoint(
                f'models/cnn_health/{self.model_type}_best.h5',
                monitor='val_accuracy',
                save_best_only=True,
                save_weights_only=False
            )
        ]
        
        # Train model
        logger.info(f"Starting training for {self.model_type} model...")
        
        self.history = self.model.fit(
            train_dataset,
            epochs=self.config['epochs'],
            validation_data=val_dataset,
            callbacks=callbacks,
            verbose=1
        )
        
        # Save final model
        model_path = f'models/cnn_health/{self.model_type}_final.h5'
        self.model.save(model_path)
        
        logger.info(f"Training completed. Model saved to {model_path}")
        
        return self.history.history
    
    def evaluate_model(self, test_dataset) -> Dict:
        """Comprehensive model evaluation"""
        
        if self.model is None:
            raise ValueError("Model not trained yet")
        
        # Get predictions
        predictions = self.model.predict(test_dataset)
        predicted_classes = np.argmax(predictions, axis=1)
        
        # Get true labels
        true_classes = test_dataset.classes
        
        # Classification report
        class_names = self.class_mappings[self.model_type]
        report = classification_report(
            true_classes, predicted_classes,
            target_names=class_names,
            output_dict=True
        )
        
        # Confusion matrix
        cm = confusion_matrix(true_classes, predicted_classes)
        
        # Calculate additional metrics
        accuracy = np.mean(predicted_classes == true_classes)
        
        evaluation_results = {
            'accuracy': accuracy,
            'classification_report': report,
            'confusion_matrix': cm.tolist(),
            'class_names': class_names,
            'model_type': self.model_type,
            'evaluation_date': datetime.now().isoformat()
        }
        
        return evaluation_results
    
    def plot_training_history(self, save_path: str = None):
        """Plot training history"""
        
        if self.history is None:
            raise ValueError("No training history available")
        
        fig, axes = plt.subplots(2, 2, figsize=(15, 10))
        
        # Accuracy
        axes[0, 0].plot(self.history.history['accuracy'], label='Training Accuracy')
        axes[0, 0].plot(self.history.history['val_accuracy'], label='Validation Accuracy')
        axes[0, 0].set_title('Model Accuracy')
        axes[0, 0].set_xlabel('Epoch')
        axes[0, 0].set_ylabel('Accuracy')
        axes[0, 0].legend()
        
        # Loss
        axes[0, 1].plot(self.history.history['loss'], label='Training Loss')
        axes[0, 1].plot(self.history.history['val_loss'], label='Validation Loss')
        axes[0, 1].set_title('Model Loss')
        axes[0, 1].set_xlabel('Epoch')
        axes[0, 1].set_ylabel('Loss')
        axes[0, 1].legend()
        
        # Precision
        if 'precision' in self.history.history:
            axes[1, 0].plot(self.history.history['precision'], label='Training Precision')
            axes[1, 0].plot(self.history.history['val_precision'], label='Validation Precision')
            axes[1, 0].set_title('Model Precision')
            axes[1, 0].set_xlabel('Epoch')
            axes[1, 0].set_ylabel('Precision')
            axes[1, 0].legend()
        
        # Recall
        if 'recall' in self.history.history:
            axes[1, 1].plot(self.history.history['recall'], label='Training Recall')
            axes[1, 1].plot(self.history.history['val_recall'], label='Validation Recall')
            axes[1, 1].set_title('Model Recall')
            axes[1, 1].set_xlabel('Epoch')
            axes[1, 1].set_ylabel('Recall')
            axes[1, 1].legend()
        
        plt.tight_layout()
        
        if save_path:
            plt.savefig(save_path, dpi=300, bbox_inches='tight')
            logger.info(f"Training plots saved to {save_path}")
        
        plt.show()
    
    def save_training_report(self, filepath: str):
        """Save comprehensive training report"""
        
        report = {
            'model_type': self.model_type,
            'training_config': self.config,
            'class_mappings': self.class_mappings[self.model_type],
            'training_date': datetime.now().isoformat(),
            'model_summary': None,
            'training_history': self.history.history if self.history else None
        }
        
        # Get model summary
        if self.model:
            import io
            stream = io.StringIO()
            self.model.summary(print_fn=lambda x: stream.write(x + '\n'))
            report['model_summary'] = stream.getvalue()
        
        with open(filepath, 'w') as f:
            json.dump(report, f, indent=2, default=str)
        
        logger.info(f"Training report saved to {filepath}")

def train_all_models():
    """Train all health analysis models"""
    
    model_types = ['skin', 'eye', 'food', 'general']
    
    for model_type in model_types:
        try:
            logger.info(f"Training {model_type} model...")
            
            trainer = AdvancedModelTrainer(model_type)
            
            # Check if training data exists
            train_dir = Path(f"data/training/{model_type}")
            if not train_dir.exists():
                logger.warning(f"No training data found for {model_type}, skipping...")
                continue
            
            # Prepare data
            train_dataset, val_dataset = trainer.prepare_data()
            
            # Create and train model
            trainer.create_model()
            history = trainer.train_model(train_dataset, val_dataset)
            
            # Save training plots and report
            trainer.plot_training_history(f"training_plots_{model_type}.png")
            trainer.save_training_report(f"training_report_{model_type}.json")
            
            logger.info(f"Successfully trained {model_type} model")
            
        except Exception as e:
            logger.error(f"Failed to train {model_type} model: {e}")

if __name__ == "__main__":
    train_all_models()