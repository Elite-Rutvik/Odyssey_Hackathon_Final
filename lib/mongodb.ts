import mongoose from 'mongoose';

if (!process.env.MONGODB_URI) {
  throw new Error('Please add your MONGODB_URI to .env.local');
}

const connectDB = async () => {
  try {
    if (mongoose.connection.readyState === 0) {
      await mongoose.connect(process.env.MONGODB_URI);
      console.log('Connected to MongoDB');
    }
  } catch (error) {
    console.error('Error connecting to MongoDB:', error);
  }
};

export default connectDB;
